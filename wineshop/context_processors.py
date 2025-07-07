# shop/context_processors.py

from .models import AddToCart, models

def cart_count(request):
    if request.user.is_authenticated:
        count = AddToCart.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0
        return {'cart_count': count}
    else:
        cart = request.session.get('cart', {})
        return {'cart_count': sum(item.get('quantity', 0) for item in cart.values())}
