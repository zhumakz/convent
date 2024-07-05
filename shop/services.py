from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _, gettext as __
from django.db import transaction
from .models import Shop, Product, Purchase
from coins.services import CoinService
from django.core.exceptions import ValidationError

class ShopService:

    @staticmethod
    def get_shops():
        return Shop.objects.all()

    @staticmethod
    def get_shop_by_id(shop_id):
        return get_object_or_404(Shop, id=shop_id)

    @staticmethod
    def get_products_by_shop(shop):
        return Product.objects.filter(shop=shop)

    @staticmethod
    def get_purchase_by_id(purchase_id):
        return get_object_or_404(Purchase, id=purchase_id)

    @staticmethod
    @transaction.atomic
    def create_purchase(seller, amount):
        purchase = Purchase(seller=seller, amount=amount)
        purchase.save()
        return purchase

    @staticmethod
    @transaction.atomic
    def complete_purchase(purchase, buyer):
        if buyer.doscointbalance.balance < purchase.amount:
            raise ValidationError(__('Недостаточно средств для завершения покупки.'))

        CoinService.create_transaction(
            sender=buyer,
            recipient=purchase.seller,
            amount=purchase.amount,
            description=__('Покупка'),
            category_name='vendor_purchase'
        )
        purchase.is_completed = True
        purchase.buyer = buyer
        purchase.save()
        return __('Покупка успешно завершена!')
