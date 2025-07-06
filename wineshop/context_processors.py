# shop/context_processors.py

def cart_count(request):
    """
    Context processor to count total quantity of items in session-based cart.
    Makes `cart_count` available in all templates.
    """
    cart = request.session.get('cart', {})
    count = sum(item.get('quantity', 0) for item in cart.values())
    return {'cart_count': count}
