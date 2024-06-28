from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext as __
import logging

logger = logging.getLogger('coins')


class DoscointBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Balance"))
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Total Earned"))

    def __str__(self):
        return f"{self.user.phone_number} - {self.balance} {__('Doscoint')}"

    class Meta:
        verbose_name = _("Doscoint Balance")
        verbose_name_plural = _("Doscoint Balances")


class Transaction(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions',
                               verbose_name=_("Sender"))
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='received_transactions', verbose_name=_("Recipient"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    is_system_transaction = models.BooleanField(default=False, verbose_name=_("Is System Transaction"))

    def save(self, *args, **kwargs):
        # Переносим всю бизнес-логику в сервисный слой
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender.phone_number} -> {self.recipient.phone_number}: {self.amount} {__('Doscoint')}"

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
