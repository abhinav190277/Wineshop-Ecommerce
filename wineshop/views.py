from django.shortcuts import render
from .models import Product, Category,DeliveryAddress
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import AddToCart, Product
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, LoginForm
from django.http import JsonResponse
import json

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
        total_price = float(request.POST.get('total_price'))
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
        cart_item.total_amount = cart_item.quantity * product.price
        cart_item.save()

    session_cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in session_cart:
        session_cart[product_id_str]['quantity'] += quantity
    else:
        session_cart[product_id_str] = {
            'quantity': quantity,
            'price': float(product.price),
        }

    request.session['cart'] = session_cart
    request.session.modified = True  

    return redirect('cart_view')

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
            else:
                return JsonResponse({"success": False, "error": "Invalid action or quantity too low."})

            item.save()
            cart = request.session.get('cart', {})
            cart_item = cart.get(str(item_id), {"quantity": item.quantity})  # ensure dict exists
            cart_item['quantity'] = item.quantity
            cart[str(item_id)] = cart_item
            request.session['cart'] = cart

            cart = request.session.get('cart', {})
            total_count = sum(item['quantity'] for item in cart.values())
            return JsonResponse({
                "success": True,
                "new_quantity": item.quantity,
                "cart_count": total_count
            })


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


import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, Product
from django.http import JsonResponse

@login_required
def checkout(request):
    if request.method == 'POST':
        cart_json = request.POST.get('cart_data')

        try:
            cart_items = json.loads(cart_json)
        except json.JSONDecodeError:
            return render(request, 'error.html', {'message': 'Invalid cart data'})

        order = Order.objects.create(customer=request.user)

        total_amount = 0

        for item in cart_items:
            try:
                product = Product.objects.get(id=item['item_id'])
                quantity = int(item['quantity'])
                item_total = product.price * quantity
                print("ppppppp",order,product)
                total_amount += item_total

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                )

            except Product.DoesNotExist:
                continue  

        order.total_amount = total_amount
        order.save()
        AddToCart.objects.filter(user=request.user).delete()
        request.session['cart'] = {}
        order_items = []
        total_amount = 0

        for item in cart_items:
            try:
                product = Product.objects.get(id=item['item_id'])
                quantity = int(item['quantity'])
                item_total = product.price * quantity
                total_amount += item_total
                
                order_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
            except Product.DoesNotExist:
                continue

        delivery_addresses = DeliveryAddress.objects.filter(user=request.user)
        default_address = delivery_addresses.filter(is_default=True).first()
        context = {
        'order_items': order_items,
        'total_amount': total_amount,
        'delivery_addresses': delivery_addresses,
        'default_address': default_address,
        }

        return render(request, 'order.html',context)  
    return redirect('cart_view')

@login_required
def add_delivery_address(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country', 'India')
        is_default = request.POST.get('is_default') == 'on'

        DeliveryAddress.objects.create(
            user=request.user,
            full_name=full_name,
            phone_number=phone_number,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default
        )

        messages.success(request, 'Address added successfully!')
        return redirect('checkout')

    return render(request, 'add_address.html')

@login_required
def edit_delivery_address(request, address_id):
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.full_name = request.POST.get('full_name')
        address.phone_number = request.POST.get('phone_number')
        address.address_line_1 = request.POST.get('address_line_1')
        address.address_line_2 = request.POST.get('address_line_2', '')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.postal_code = request.POST.get('postal_code')
        address.country = request.POST.get('country', 'India')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()

        messages.success(request, 'Address updated successfully!')
        return redirect('confirm_order')

    return re
   







