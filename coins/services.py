from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, gettext as __
from .models import DoscointBalance, Transaction
import logging

logger = logging.getLogger('coins')

class CoinService:

    @staticmethod
    def create_transaction(sender, recipient, amount, description="", is_system_transaction=False):
        with db_transaction.atomic():
            if amount <= 0:
                logger.error(f'Transaction amount must be positive: {amount}')
                raise ValidationError(__("Transaction amount must be positive"))

            if not is_system_transaction and sender.doscointbalance.balance < amount:
                logger.error(f'Sender does not have enough balance: {sender.doscointbalance.balance}')
                raise ValidationError(__("Sender does not have enough balance"))

            if sender.groups.filter(name='AddModerators').exists() and amount > 10:
                logger.error(f'AddModerators cannot send more than 10 coins per transaction: {amount}')
                raise ValidationError(__("AddModerators cannot send more than 10 coins per transaction"))

            if sender.groups.filter(name='RemoveModerators').exists() and recipient.doscointbalance.balance - amount < 0:
                logger.error(f'RemoveModerators cannot reduce balance below 0: {recipient.doscointbalance.balance}')
                raise ValidationError(__("RemoveModerators cannot reduce balance below 0"))

            # Update sender balance if not system transaction
            if not is_system_transaction:
                logger.debug(f'Updating sender balance: {sender.doscointbalance.balance} - {amount}')
                sender.doscointbalance.balance -= amount
                sender.doscointbalance.save()

            # Update recipient balance
            logger.debug(f'Updating recipient balance: {recipient.doscointbalance.balance} + {amount}')
            recipient.doscointbalance.balance += amount
            recipient.doscointbalance.total_earned += amount
            recipient.doscointbalance.save()

            # Create transaction record
            transaction = Transaction(
                sender=sender,
                recipient=recipient,
                amount=amount,
                description=description,
                is_system_transaction=is_system_transaction
            )
            transaction.save()

            logger.debug(f'Transaction created: {transaction}')
            return transaction

    @staticmethod
    def get_balance(user):
        return user.doscointbalance.balance

    @staticmethod
    def get_transactions(user):
        return Transaction.objects.filter(sender=user) | Transaction.objects.filter(recipient=user)

    @staticmethod
    def process_transaction(transaction, user):
        if transaction.is_system_transaction:
            transaction.sender_name = __("System")
            transaction.recipient_name = f"{transaction.recipient.name} {transaction.recipient.surname}"
        else:
            if transaction.sender == user:
                transaction.sender_name = __("You")
            else:
                if transaction.sender.is_superuser:
                    transaction.sender_name = __("System")
                elif transaction.sender.groups.filter(name__in=['AddModerators', 'RemoveModerators']).exists():
                    transaction.sender_name = f"{transaction.sender.name} {transaction.sender.surname}"
                else:
                    transaction.sender_name = transaction.sender.phone_number

            if transaction.recipient == user:
                transaction.recipient_name = __("You")
            else:
                transaction.recipient_name = f"{transaction.recipient.name} {transaction.recipient.surname}"
        return transaction
