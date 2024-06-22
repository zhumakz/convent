from django.contrib import admin
from .models import Shop, Product, Purchase

class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'owner']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description', 'shop']

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['seller', 'buyer', 'shop', 'amount', 'is_completed', 'created_at']
    list_filter = ['created_at']

admin.site.register(Shop, ShopAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
