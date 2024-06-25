# shop/admin.py
from django.contrib import admin
from .models import Shop, Product, Purchase

class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'price')

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'seller', 'amount', 'created_at', 'is_completed')
    search_fields = ('buyer__phone_number', 'seller__phone_number')

admin.site.register(Shop, ShopAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
