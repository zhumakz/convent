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
        self.balance = models.F('balance') + amount
        self.save(update_fields=['balance'])

    def increment_total_earned(self, amount):
        self.total_earned = models.F('total_earned') + amount
        self.save(update_fields=['total_earned'])

    def increment_total_spent(self, amount):
        self.total_spent = models.F('total_spent') + amount
        self.save(update_fields=['total_spent'])

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
        ('new_category', _("New Category")),
    ]

    name = models.CharField(max_length=30, choices=CATEGORY_CHOICES, unique=True, verbose_name=_("Name"))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name=_("Price"))
    display_name = models.CharField(max_length=100, verbose_name=_("Display Name"), default="")

    def __str__(self):
        return f"{self.display_name} - {__('Price')}"

    class Meta:
        verbose_name = _("Transaction Category")
        verbose_name_plural = _("Transaction Categories")

    @staticmethod
    def create_default_categories():
        categories = [
            {'name': 'friend_bonus_same_city', 'price': 1, 'display_name_ru': 'Бонус за друга (тот же город)',
             'display_name_kk': 'Дос үшін бонус (сол қала)'},
            {'name': 'friend_bonus_different_city', 'price': 2, 'display_name_ru': 'Бонус за друга (другой город)',
             'display_name_kk': 'Дос үшін бонус (басқа қала)'},
            {'name': 'lecture_bonus', 'price': 5, 'display_name_ru': 'Бонус за лекцию',
             'display_name_kk': 'Дәріс үшін бонус'},
            {'name': 'event_bonus', 'price': 3, 'display_name_ru': 'Бонус за мероприятие',
             'display_name_kk': 'Іс-шара үшін бонус'},
            {'name': 'vote_bonus', 'price': 1, 'display_name_ru': 'Бонус за голосование',
             'display_name_kk': 'Дауыс беру үшін бонус'},
            {'name': 'moderator_transfer', 'price': 0, 'display_name_ru': 'Перевод модератора',
             'display_name_kk': 'Модератор аударымы'},
            {'name': 'vendor_purchase', 'price': 0, 'display_name_ru': 'Покупка у продавца',
             'display_name_kk': 'Сатушыдан сатып алу'},
            {'name': 'new_category', 'price': 0, 'display_name_ru': 'Новая категория', 'display_name_kk': 'Жаңа санат'},
        ]

        for category in categories:
            TransactionCategory.objects.update_or_create(
                name=category['name'],
                defaults={
                    'price': category['price'],
                    'display_name_ru': category['display_name_ru'],
                    'display_name_kk': category['display_name_kk']
                }
            )


class Transaction(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions', verbose_name=_("Sender"))
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_transactions', verbose_name=_("Recipient"))
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
