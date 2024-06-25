import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Shop, Product, Purchase
from .forms import ProductForm, PurchaseForm
from coins.models import Transaction

def is_moderator(user):
    return user.is_authenticated and user.is_moderator

@login_required
def shop_list(request):
    shops = Shop.objects.all()
    return render(request, 'shop/shop_list.html', {'shops': shops})

@login_required
def product_list(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    products = Product.objects.filter(shop=shop)
    return render(request, 'shop/product_list.html', {'shop': shop, 'products': products})

@login_required
@user_passes_test(is_moderator)
def add_product(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_list', shop_id=shop_id)
    else:
        form = ProductForm()
    return render(request, 'shop/add_product.html', {'form': form, 'shop': shop})

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
            return render(request, 'shop/generate_purchase_qr.html', {'purchase': purchase})
    else:
        form = PurchaseForm()
    return render(request, 'shop/generate_purchase_qr.html', {'form': form})

@login_required
def scan_qr(request, qr_data):
    try:
        qr_data = json.loads(qr_data)
        purchase_id = qr_data.get("purchase_id")
        purchase = get_object_or_404(Purchase, id=purchase_id)
        buyer = request.user
        if buyer.doscointbalance.balance < purchase.amount:
            messages.error(request, 'Insufficient balance to complete the purchase.')
            return redirect('product_list', shop_id=purchase.product.shop.id)

        Transaction.objects.create(
            sender=buyer,
            recipient=purchase.seller,
            amount=purchase.amount,
            description=f'Purchase in {purchase.product.shop.name}'
        )
        purchase.is_completed = True
        purchase.buyer = buyer
        purchase.save()

        messages.success(request, 'Purchase completed successfully!')
        return redirect('product_list', shop_id=purchase.product.shop.id)
    except Exception as e:
        messages.error(request, 'Invalid QR code or purchase data.')
        return redirect('shop_list')
