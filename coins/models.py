from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext as __
import logging

logger = logging.getLogger('coins')


class DoscointBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Balance"))
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Total Earned"))
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Total Spent"))

    def __str__(self):
        return f"{self.user.phone_number} - {self.balance} {__('Doscoint')}"

    def update_balance(self, amount):
        self.balance += amount
        self.save()

    class Meta:
        verbose_name = _("Doscoint Balance")
        verbose_name_plural = _("Doscoint Balances")


class TransactionCategory(models.Model):
    CATEGORY_CHOICES = [
        ('friend_bonus_same_city', _("Friend Bonus (Same City)")),
        ('friend_bonus_different_city', _("Friend Bonus (Different City)")),
        ('lecture_bonus', _("Lecture Bonus")),
        ('event_bonus', _("Event Bonus")),
        ('vote_bonus', _("Vote Bonus")),
        ('moderator_transfer', _("Moderator Transfer")),
        ('vendor_purchase', _("Vendor Purchase")),
        ('new_category', _("New Category")),  # Добавляем новый тип категории
    ]

    name = models.CharField(max_length=30, choices=CATEGORY_CHOICES, unique=True, verbose_name=_("Name"))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name=_("Price"))
    display_name = models.CharField(max_length=100, verbose_name=_("Display Name"), default="")  # Добавляем новое поле

    def __str__(self):
        return f"{self.display_name} - {__('Price')}"

    class Meta:
        verbose_name = _("Transaction Category")
        verbose_name_plural = _("Transaction Categories")

    @staticmethod
    def create_default_categories():
        categories = [
            {'name': 'friend_bonus_same_city', 'price': 1, 'display_name': _("Friend Bonus (Same City)")},
            {'name': 'friend_bonus_different_city', 'price': 2, 'display_name': _("Friend Bonus (Different City)")},
            {'name': 'lecture_bonus', 'price': 5, 'display_name': _("Lecture Bonus")},
            {'name': 'event_bonus', 'price': 3, 'display_name': _("Event Bonus")},
            {'name': 'vote_bonus', 'price': 1, 'display_name': _("Vote Bonus")},
            {'name': 'moderator_transfer', 'price': 0, 'display_name': _("Moderator Transfer")},
            {'name': 'vendor_purchase', 'price': 0, 'display_name': _("Vendor Purchase")},
            {'name': 'new_category', 'price': 0, 'display_name': _("New Category")},  # Добавляем новый тип категории
        ]

        for category in categories:
            TransactionCategory.objects.get_or_create(name=category['name'], defaults={'price': category['price'], 'display_name': category['display_name']})



class Transaction(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions',
                               verbose_name=_("Sender"))
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='received_transactions', verbose_name=_("Recipient"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE, verbose_name=_("Category"), default=1)
    is_positive = models.BooleanField(default=True, verbose_name=_("Is Positive"))

    def __str__(self):
        return f"{self.sender.phone_number} -> {self.recipient.phone_number}: {self.amount} {__('Doscoint')}"

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
