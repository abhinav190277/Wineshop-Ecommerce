from django.shortcuts import render
from .models import Product, Category
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import AddToCart, Product

def home(request):
    return render(request, 'home.html')



def shop_page(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': query,
    }
    return render(request, 'shop.html', context)    



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = AddToCart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1  
    cart_item.save()  

    return redirect('shop')  


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

@login_required
def update_qty(request, item_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            action = data.get("action")

            item = AddToCart.objects.get(id=item_id, user=request.user)

            if action == "increase":
                item.quantity += 1
            elif action == "decrease" and item.quantity > 1:
                item.quantity -= 1

            item.save()
            return JsonResponse({"success": True, "new_quantity": item.quantity})
        except AddToCart.DoesNotExist:
            return JsonResponse({"success": False, "error": "Item not found."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method."})

@login_required
def cart_view(request):
    items = AddToCart.objects.filter(user=request.user)
    total = sum(item.total_amount for item in items)
    return render(request, 'cart.html', {'items': items, 'total': total})

