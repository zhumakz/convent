from django import forms
from .models import Product, Purchase


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description']


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['shop', 'amount']
