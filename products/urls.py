from django.urls import path
from . import views

urlpatterns = [
    # trang chủ
    path('', views.home, name='home'),
    
    # chi tiết sản phẩm và đánh giá 
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),

    # giỏ hàng
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:product_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # thanh toán và đơn hàng
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('success/<int:order_id>/', views.success, name='success'),

    # tài khoản và hồ sơ
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    #admin dashboard, Dành cho quản lý
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('update-status/<int:order_id>/<str:new_status>/', views.update_status, name='update_status'),
    path('admin-delete-order/<int:order_id>/', views.admin_delete_order, name='admin_delete_order'),

    # Quản lý kho hàng (Thêm, Sửa, Xóa Sản phẩm)
    path('admin-dashboard/products/', views.manage_products, name='manage_products'),
    path('admin-dashboard/add-product/', views.add_product, name='add_product'),
    path('admin-dashboard/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('admin-dashboard/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
]