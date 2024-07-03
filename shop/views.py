from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .services import ShopService
from .forms import PurchaseForm
import json

def is_moderator(user):
    return user.is_authenticated and user.is_moderator

@login_required
def shop_list(request):
    shops = ShopService.get_shops()
    return render(request, 'shop/shop_list.html', {'shops': shops})

@login_required
def product_list(request, shop_id):
    shop = ShopService.get_shop_by_id(shop_id)
    products = ShopService.get_products_by_shop(shop)
    return render(request, 'shop/product_list.html', {'shop': shop, 'products': products})

@login_required
@user_passes_test(is_moderator)
def generate_purchase_qr(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.seller = request.user
            purchase.save()

            messages.success(request, 'QR code generated successfully!')
            return redirect('product_list', shop_id=purchase.seller.shop_set.first().id)
    else:
        form = PurchaseForm()
    return render(request, 'shop/generate_purchase_qr.html', {'form': form})