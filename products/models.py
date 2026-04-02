from django.db import models
from django.contrib.auth.models import User

# danh mục (điện thoại, Laptop...)
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

# sản phẩm
class Product(models.Model):
    category = models.ForeignKey(Category,  on_delete=models.CASCADE, related_name='products',  verbose_name="Danh mục")
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá tiền")
    image = models.ImageField(upload_to='products/', verbose_name="Hình ảnh")
    description = models.TextField(blank=True, verbose_name="Mô tả chi tiết")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# đơn hàng Lưu thông tin mua sắm
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50, default='Chờ xử lý')
    full_name = models.CharField(max_length=200, verbose_name="Họ tên")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ giao hàng")
    total_price = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    items_json = models.TextField() 

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.full_name}"

# hồ sơ cá nhân 
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, verbose_name="Địa chỉ mặc định")

    def __str__(self):
        return f"Hồ sơ của {self.user.username}"

# đánh giá sản phẩm
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5, verbose_name="Số sao")
    comment = models.TextField(verbose_name="Nội dung đánh giá")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} đánh giá {self.product.name}"