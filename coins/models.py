from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class DoscointBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.phone_number} - {self.balance} Доскойн"


import logging

logger = logging.getLogger('coins')


class Transaction(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    is_system_transaction = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        logger.debug(f'Saving transaction: {self.sender} -> {self.recipient} : {self.amount}')
        if self.amount <= 0:
            logger.error(f'Transaction amount must be positive: {self.amount}')
            raise ValidationError("Transaction amount must be positive")

        if not self.is_system_transaction and self.sender.doscointbalance.balance < self.amount:
            logger.error(f'Sender does not have enough balance: {self.sender.doscointbalance.balance}')
            raise ValidationError("Sender does not have enough balance")

        if self.sender.groups.filter(name='AddModerators').exists() and self.amount > 10:
            logger.error(f'AddModerators cannot send more than 10 coins per transaction: {self.amount}')
            raise ValidationError("AddModerators cannot send more than 10 coins per transaction")

        if self.sender.groups.filter(
                name='RemoveModerators').exists() and self.recipient.doscointbalance.balance - self.amount < 0:
            logger.error(f'RemoveModerators cannot reduce balance below 0: {self.recipient.doscointbalance.balance}')
            raise ValidationError("RemoveModerators cannot reduce balance below 0")

        if not self.is_system_transaction:
            logger.debug(f'Updating sender balance: {self.sender.doscointbalance.balance} - {self.amount}')
            self.sender.doscointbalance.balance -= self.amount
            self.sender.doscointbalance.save()

        logger.debug(f'Updating recipient balance: {self.recipient.doscointbalance.balance} + {self.amount}')
        self.recipient.doscointbalance.balance += self.amount
        self.recipient.doscointbalance.total_earned += self.amount
        self.recipient.doscointbalance.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender.phone_number} -> {self.recipient.phone_number}: {self.amount} Доскойн"
