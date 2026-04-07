from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
import json
from .forms import ProductForm

# Import các Model cốt lõi
from .models import Product, Order, Category, Profile, Review

# ==========================================
# PHÂN HỆ KHÁCH HÀNG & TRANG CHỦ
# ==========================================
def home(request):
    """Trang chủ hiển thị danh sách sản phẩm kèm lọc theo giá và tìm kiếm AJAX."""
    products = Product.objects.all().order_by('-created_at')
    
    # Xử lý Tìm kiếm Search
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Xử lý Lọc theo danh mục Category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Xử lý Lọc theo mức giá
    price_range = request.GET.get('price')
    if price_range == 'under-10':
        products = products.filter(price__lt=10000000)
    elif price_range == '10-20':
        products = products.filter(price__gte=10000000, price__lte=20000000)
    elif price_range == 'over-20':
        products = products.filter(price__gt=20000000)

    # Trả về dữ liệu AJAX cho Live Search
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('products/product_list_partial.html', {'products': products}, request=request)
        return JsonResponse({'html': html})

    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'category_slug': category_slug,
    }
    return render(request, 'products/home.html', context)

def product_detail(request, pk):
    """Trang chi tiết sản phẩm kèm danh sách đánh giá từ khách hàng."""
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all().order_by('-created_at')
    return render(request, 'products/detail.html', {'product': product, 'reviews': reviews})

@login_required(login_url='login')
def add_review(request, product_id):
    """Xử lý hành động khách hàng gửi đánh giá mới."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        Review.objects.create(
            product=product,
            user=request.user,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )
        messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm!")
    return redirect('product_detail', pk=product_id)

@login_required(login_url='login')
def profile_view(request):
    """Trang cập nhật thông tin cá nhân (SĐT, Địa chỉ)."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.save()
        messages.success(request, "Hồ sơ của bạn đã được cập nhật!")
        return redirect('profile')
    return render(request, 'products/profile.html', {'profile': profile})

# ==========================================
# PHÂN HỆ GIỎ HÀNG & THANH TOÁN (ĐÃ NÂNG CẤP)
# ==========================================
@login_required(login_url='login')
def add_to_cart(request, product_id):
    """Thêm sản phẩm vào giỏ kèm tùy chọn Số lượng và Màu sắc."""
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    
    # Lấy dữ liệu từ Form (Mặc định số lượng là 1 nếu không có)
    quantity = int(request.GET.get('quantity', 1))
    color = request.GET.get('color', 'Mặc định')
    action = request.GET.get('action')

    if p_id in cart:
        # Nếu giỏ hàng cũ lưu dạng số, chuyển sang dạng Dictionary
        if isinstance(cart[p_id], int):
            cart[p_id] = {'quantity': cart[p_id] + quantity, 'color': color}
        else:
            cart[p_id]['quantity'] += quantity
            cart[p_id]['color'] = color
    else:
        cart[p_id] = {'quantity': quantity, 'color': color}

    request.session['cart'] = cart
    request.session.modified = True

    if action == 'checkout':
        return redirect('checkout')
    messages.success(request, f"Đã thêm {quantity} sản phẩm vào giỏ hàng!")
    return redirect(request.META.get('HTTP_REFERER', '/'))

def cart_detail(request):
    """Hiển thị toàn bộ giỏ hàng (Hỗ trợ đọc màu sắc)."""
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for p_id, item_data in cart.items():
        product = get_object_or_404(Product, id=p_id)
        
        # Kiểm tra tương thích ngược
        if isinstance(item_data, int):
            q = item_data
            color = "Mặc định"
        else:
            q = item_data.get('quantity', 1)
            color = item_data.get('color', 'Mặc định')
            
        total = product.price * q
        total_price += total
        cart_items.append({
            'product': product, 
            'quantity': q, 
            'color': color,
            'total': total
        })
        
    return render(request, 'products/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def update_cart(request, product_id, action):
    """Tăng/Giảm hoặc xóa sản phẩm trong giỏ hàng."""
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    
    if p_id in cart:
        # Chuyển đổi nếu là giỏ hàng kiểu cũ
        if isinstance(cart[p_id], int):
            cart[p_id] = {'quantity': cart[p_id], 'color': 'Mặc định'}
            
        if action == 'increment': 
            cart[p_id]['quantity'] += 1
        elif action == 'decrement':
            if cart[p_id]['quantity'] > 1: 
                cart[p_id]['quantity'] -= 1
            else: 
                del cart[p_id]
                
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

def remove_from_cart(request, product_id):
    """Xóa hoàn toàn một món khỏi giỏ hàng."""
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
        messages.warning(request, "Đã xóa sản phẩm khỏi giỏ.")
    return redirect('cart_detail')

@login_required(login_url='login')
def checkout(request):
    """Trang thanh toán tự in Màu sắc vào hóa đơn."""
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        total_price = 0
        items_for_json = []
        for p_id, item_data in cart.items():
            product = get_object_or_404(Product, id=p_id)
            
            if isinstance(item_data, int):
                q = item_data
                color = "Mặc định"
            else:
                q = item_data.get('quantity', 1)
                color = item_data.get('color', 'Mặc định')
                
            total_price += product.price * q
            
            # Gắn màu sắc thẳng vào tên sản phẩm để lưu Database
            full_name = f"{product.name} ({color})" if color != "Mặc định" else product.name
            
            items_for_json.append({
                'id': product.id, 
                'name': full_name,
                'price': float(product.price), 
                'quantity': q,
                'total': float(product.price * q),
                'image_url': product.image.url if product.image else ''
            })

        order = Order.objects.create(
            user=request.user, 
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'), 
            address=request.POST.get('address'),
            total_price=total_price, 
            items_json=json.dumps(items_for_json)
        )
        
        request.session['cart'] = {}
        request.session.modified = True
        
        messages.success(request, f"Đặt hàng thành công! Mã đơn: #{order.id}")
        return redirect('success', order_id=order.id)

    cart_items = []
    total_price = 0
    for p_id, item_data in cart.items():
        product = get_object_or_404(Product, id=p_id)
        
        if isinstance(item_data, int):
            q = item_data
            color = "Mặc định"
        else:
            q = item_data.get('quantity', 1)
            color = item_data.get('color', 'Mặc định')
            
        total_price += product.price * q
        full_name = f"{product.name} ({color})" if color != "Mặc định" else product.name
        
        cart_items.append({'name': full_name, 'quantity': q, 'total': product.price * q, 'image_url': product.image.url})

    return render(request, 'products/checkout.html', {'cart_items': cart_items, 'total_price': total_price, 'profile': profile})

@login_required(login_url='login')
def success(request, order_id):
    """Trang thông báo đặt hàng thành công kèm chi tiết hóa đơn."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.parsed_items = json.loads(order.items_json) if order.items_json else []
    return render(request, 'products/success.html', {'order': order})

# ==========================================
# PHÂN HỆ QUẢN TRỊ VIÊN (ADMIN)
# ==========================================
@staff_member_required(login_url='login')
def admin_dashboard(request):
    """Dashboard dành cho Admin: Quản lý đơn hàng + Xem biểu đồ doanh thu."""
    orders = Order.objects.all().order_by('-created_at')
    
    sales_data = Order.objects.filter(status='Hoàn thành') \
        .annotate(date=TruncDate('created_at')) \
        .values('date') \
        .annotate(total=Sum('total_price')) \
        .order_by('date')

    chart_labels = [d['date'].strftime("%d/%m") for d in sales_data]
    chart_values = [float(d['total']) for d in sales_data]

    for order in orders:
        order.parsed_items = json.loads(order.items_json) if order.items_json else []
        
    context = {
        'orders': orders,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_values),
        'total_revenue': sum(chart_values)
    }
    return render(request, 'products/admin_dashboard.html', context)

@staff_member_required(login_url='login')
def update_status(request, order_id, new_status):
    """Admin cập nhật trạng thái đơn hàng."""
    order = get_object_or_404(Order, id=order_id)
    order.status = new_status
    order.save()
    messages.success(request, f"Đơn #{order_id} chuyển sang: {new_status}")
    return redirect('admin_dashboard')

@staff_member_required(login_url='login')
def admin_delete_order(request, order_id):
    """Admin xóa vĩnh viễn đơn hàng."""
    get_object_or_404(Order, id=order_id).delete()
    messages.info(request, "Đã xóa đơn hàng khỏi hệ thống.")
    return redirect('admin_dashboard')

@staff_member_required(login_url='login')
def add_product(request):
    """Trang dành cho Admin thêm sản phẩm mới vào hệ thống."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã thêm sản phẩm thành công!")
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

@staff_member_required(login_url='login')
def manage_products(request):
    """Trang liệt kê tất cả sản phẩm để dễ quản lý."""
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/manage_products.html', {'products': products})

@staff_member_required(login_url='login')
def edit_product(request, pk):
    """Trang sửa thông tin sản phẩm đã có."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Đã cập nhật {product.name} thành công!")
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/add_product.html', {'form': form, 'edit_mode': True, 'product': product})

@staff_member_required(login_url='login')
def delete_product(request, pk):
    """Xóa vĩnh viễn sản phẩm khỏi kho."""
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.warning(request, f"Đã xóa sản phẩm {product.name}!")
    return redirect('manage_products')

# ==========================================
# PHÂN HỆ TÀI KHOẢN & LỊCH SỬ ĐƠN HÀNG
# ==========================================
def register_view(request):
    if request.method == 'POST':
        u, p, pc = request.POST.get('username'), request.POST.get('password'), request.POST.get('password_confirm')
        if p == pc and not User.objects.filter(username=u).exists():
            user = User.objects.create_user(u, password=p)
            login(request, user)
            return redirect('home')
    return render(request, 'products/register.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    return render(request, 'products/login.html', {'form': AuthenticationForm()})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def my_orders(request):
    """Trang lịch sử mua hàng của cá nhân User."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    for order in orders:
        order.parsed_items = json.loads(order.items_json) if order.items_json else []
    return render(request, 'products/my_orders.html', {'orders': orders})

@login_required(login_url='login')
def cancel_order(request, order_id):
    """Hủy đơn hàng nếu đang chờ xử lý."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'Chờ xử lý':
        order.status = 'Đã hủy'
        order.save()
        messages.success(request, "Đã hủy đơn hàng thành công.")
    return redirect('my_orders')

@login_required(login_url='login')
def delete_order(request, order_id):
    """Xóa đơn hàng khỏi lịch sử (Chỉ khi đã hoàn thành hoặc hủy)."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ['Đã hủy', 'Hoàn thành']:
        order.delete()
        messages.info(request, "Đã xóa đơn hàng khỏi lịch sử.")
    else:
        messages.error(request, "Không thể xóa đơn hàng đang giao!")
    return redirect('my_orders')