from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, gettext as __
from .models import DoscointBalance, Transaction, TransactionCategory
import logging

logger = logging.getLogger('coins')

class CoinService:

    @staticmethod
    def validate_transaction(sender, amount, category):
        if amount <= 0:
            logger.error(f'Transaction amount must be positive: {amount}')
            raise ValidationError(__("Transaction amount must be positive"))

        if category.name not in ['friend_bonus_same_city', 'friend_bonus_different_city', 'lecture_bonus', 'event_bonus', 'vote_bonus'] and sender.doscointbalance.balance < amount:
            logger.error(f'Sender does not have enough balance: {sender.doscointbalance.balance}')
            raise ValidationError(__("Sender does not have enough balance"))

    @staticmethod
    def update_balances(sender, recipient, amount, category):
        if category.name not in ['friend_bonus_same_city', 'friend_bonus_different_city', 'lecture_bonus', 'event_bonus', 'vote_bonus']:
            sender.doscointbalance.update_balance(-amount)
            sender.doscointbalance.save()
        recipient.doscointbalance.update_balance(amount)
        recipient.doscointbalance.save()

    @staticmethod
    def update_total_earned(user, amount):
        user.doscointbalance.total_earned += amount
        user.doscointbalance.save()

    @staticmethod
    def update_total_spent(user, amount):
        user.doscointbalance.total_spent += amount
        user.doscointbalance.save()

    @staticmethod
    def create_transaction(sender, recipient, amount=None, description="", category_name=""):
        with db_transaction.atomic():
            category = TransactionCategory.objects.get(name=category_name)
            if category.name in ['friend_bonus_same_city', 'friend_bonus_different_city', 'lecture_bonus', 'event_bonus', 'vote_bonus']:
                amount = category.price
            else:
                if amount is None:
                    raise ValidationError(__("Amount must be provided for non-system transactions"))

            CoinService.validate_transaction(sender, amount, category)
            CoinService.update_balances(sender, recipient, amount, category)

            if category.name not in ['friend_bonus_same_city', 'friend_bonus_different_city', 'lecture_bonus', 'event_bonus', 'vote_bonus']:
                CoinService.update_total_spent(sender, amount)
            CoinService.update_total_earned(recipient, amount)

            transaction = Transaction(
                sender=sender,
                recipient=recipient,
                amount=amount,
                description=description,
                category=category,
                is_positive=(sender != recipient)
            )
            transaction.save()

            logger.debug(f'Transaction created: {transaction}')
            return transaction

    @staticmethod
    def get_balance(user):
        return user.doscointbalance.balance

    @staticmethod
    def get_total_earned(user):
        return user.doscointbalance.total_earned

    @staticmethod
    def get_total_spent(user):
        return user.doscointbalance.total_spent

    @staticmethod
    def get_transactions(user):
        return Transaction.objects.filter(sender=user) | Transaction.objects.filter(recipient=user)
