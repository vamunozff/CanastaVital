from carton.cart import Cart

def cart_count(request):
    cart = Cart(request.session)
    count = sum(item.quantity for item in cart.items)
    return {'cart_count': count}
