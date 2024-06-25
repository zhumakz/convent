from django.contrib import admin
from .models import Shop, Product, Purchase

class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'price')
    search_fields = ('name', 'shop__name')

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'seller', 'amount', 'created_at', 'is_completed')
    search_fields = ('buyer__phone_number', 'seller__phone_number')
    actions = ['generate_qr_codes']

    def generate_qr_codes(self, request, queryset):
        for purchase in queryset:
            purchase.generate_qr_code()
            purchase.save()
        self.message_user(request, "QR codes generated successfully.")

    generate_qr_codes.short_description = "Generate QR codes for selected purchases"

admin.site.register(Shop, ShopAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
