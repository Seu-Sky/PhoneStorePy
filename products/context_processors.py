def cart_count(request):
    # Lấy giỏ hàng từ session
    cart = request.session.get('cart', {})
    
    # Tính tổng số lượng (values là danh sách các số lượng của từng món)
    count = sum(cart.values())
    return {'cart_count': count}
