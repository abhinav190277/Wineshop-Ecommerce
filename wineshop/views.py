from django.shortcuts import render
from .models import Product, Category
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import AddToCart, Product
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, LoginForm

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
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    try:
        total_price = float(request.POST.get('total_price', 0.0))
    except (ValueError, TypeError):
        total_price = product.price * quantity  

    cart_item, created = AddToCart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={
            'quantity': quantity,
            'total_amount': total_price,  
        }
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.total_price = cart_item.quantity * product.price  
        cart_item.save()

    return redirect('cart_view')

  


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

@login_required


def update_qty(request, item_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            action = data.get("action")

            # Update in DB
            item = AddToCart.objects.get(id=item_id, user=request.user)

            if action == "increase":
                item.quantity += 1
            elif action == "decrease" and item.quantity > 1:
                item.quantity -= 1
            else:
                return JsonResponse({"success": False, "error": "Invalid action or quantity too low."})

            item.save()

            # Sync session cart
            cart = request.session.get('cart', {})
            cart_item = cart.get(str(item_id), {"quantity": item.quantity})  # ensure dict exists
            cart_item['quantity'] = item.quantity
            cart[str(item_id)] = cart_item
            request.session['cart'] = cart

            return JsonResponse({"success": True, "new_quantity": item.quantity})

        except AddToCart.DoesNotExist:
            return JsonResponse({"success": False, "error": "Item not found."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})


@login_required
def remove_qty(request, item_id):
    if request.method == "POST":
        try:
            item = AddToCart.objects.get(id=item_id, user=request.user)
            item.delete()  
            return JsonResponse({"success": True})
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

@login_required
def product_detail(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})



from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if not username or not email or not password or not confirm_password:
            messages.error(request, 'Please fill in all fields.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')  

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')







