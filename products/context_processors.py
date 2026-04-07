
def cart_count(request):
    """Đếm tổng số lượng sản phẩm trong giỏ hàng (Hỗ trợ giỏ hàng có màu sắc)."""
    cart = request.session.get('cart', {})
    count = 0
    
    for item_data in cart.values():
        # Nếu là giỏ hàng kiểu cũ (chỉ có số nguyên)
        if isinstance(item_data, int):
            count += item_data
        # Nếu là giỏ hàng kiểu mới (có từ điển chứa quantity và color)
        else:
            count += item_data.get('quantity', 0)
            
    return {'cart_count': count}