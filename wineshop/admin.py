from django.contrib import admin
from .models import Vendor, Category, Product, ProductImage, Review, Order, OrderItem, AddToCart,DeliveryAddress

admin.site.register(Vendor)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(AddToCart)
admin.site.register(DeliveryAddress)


