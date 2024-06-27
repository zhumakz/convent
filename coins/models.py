from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, gettext as __
import logging

logger = logging.getLogger('coins')

class DoscointBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.phone_number} - {self.balance} {__('Doscoint')}"

class Transaction(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    is_system_transaction = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Переносим всю бизнес-логику в сервисный слой
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender.phone_number} -> {self.recipient.phone_number}: {self.amount} {__('Doscoint')}"
