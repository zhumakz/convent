from django.contrib import admin
from .models import Shop, Product, Purchase


class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'owner']
    search_fields = ['name', 'address', 'owner__phone_number']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'shop']
    search_fields = ['name', 'shop__name']
    list_filter = ['shop']


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'seller', 'product', 'amount', 'timestamp', 'is_completed']
    search_fields = ['buyer__phone_number', 'seller__phone_number', 'product__name']
    list_filter = ['timestamp', 'is_completed']


admin.site.register(Shop, ShopAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
