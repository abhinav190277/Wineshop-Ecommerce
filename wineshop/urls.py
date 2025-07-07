from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop_page, name='shop'),
    path('my-cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('update_qty/<int:item_id>/', views.update_qty, name='update_qty'),
    path('remove-item/<int:item_id>/', views.remove_qty, name='remove_qty'),
    path('product-detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('checkout/', views.checkout, name='checkout'),
    path('add-address/', views.add_delivery_address, name='add_address'),
    path('edit-address/<int:address_id>/', views.edit_delivery_address, name='edit_address'),


]