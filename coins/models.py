from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class DoscointBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.phone_number} - {self.balance} Доскойн"


class Transaction(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.amount <= 0:
            raise ValidationError("Transaction amount must be positive")
        if self.sender.doscointbalance.balance < self.amount:
            raise ValidationError("Sender does not have enough balance")

        self.sender.doscointbalance.balance -= self.amount
        self.sender.doscointbalance.save()

        self.recipient.doscointbalance.balance += self.amount
        self.recipient.doscointbalance.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender.phone_number} -> {self.recipient.phone_number}: {self.amount} Доскойн"
