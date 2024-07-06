from django.core.cache import cache
from django.db import transaction as db_transaction, models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, gettext as __
from .models import DoscointBalance, Transaction, TransactionCategory
import logging

logger = logging.getLogger('coins')


class CoinService:

    @staticmethod
    def validate_transaction(sender, amount, category):
        if amount <= 0:
            logger.error(f'Сумма транзакции должна быть положительной: {amount}')
            raise ValidationError(__("Сумма транзакции должна быть положительной"))

        if category.name not in ['friend_bonus_same_city', 'friend_bonus_different_city', 'lecture_bonus',
                                 'event_bonus', 'vote_bonus'] and sender.doscointbalance.balance < amount:
            logger.error(f'У отправителя недостаточно средств: {sender.doscointbalance.balance}')
            raise ValidationError(__("У отправителя недостаточно средств"))

    @staticmethod
    def update_balances(sender, recipient, amount, category):
        if category.name not in ['friend_bonus_same_city', 'friend_bonus_different_city', 'lecture_bonus',
                                 'event_bonus', 'vote_bonus']:
            sender.doscointbalance.update_balance(-amount)
        recipient.doscointbalance.update_balance(amount)

    @staticmethod
    def update_total_earned(user, amount):
        user.doscointbalance.increment_total_earned(amount)

    @staticmethod
    def update_total_spent(user, amount):
        user.doscointbalance.increment_total_spent(amount)

    @staticmethod
    def create_transaction(sender, recipient, amount=None, description="", category_name=""):
        with db_transaction.atomic():
            category = TransactionCategory.objects.get(name=category_name)
            if category.name in ['friend_bonus_same_city', 'friend_bonus_different_city', 'lecture_bonus',
                                 'event_bonus', 'vote_bonus']:
                amount = category.price
            elif amount is None:
                raise ValidationError(__("Сумма должна быть указана для несистемных транзакций"))

            CoinService.validate_transaction(sender, amount, category)
            CoinService.update_balances(sender, recipient, amount, category)

            if category.name not in ['friend_bonus_same_city', 'friend_bonus_different_city', 'lecture_bonus',
                                     'event_bonus', 'vote_bonus']:
                sender.doscointbalance.increment_total_spent(amount)
            recipient.doscointbalance.increment_total_earned(amount)

            transaction = Transaction(
                sender=sender,
                recipient=recipient,
                amount=amount,
                description=description,
                category=category,
                is_positive=(sender != recipient)
            )
            transaction.save()
            # Очистка кэша для пользователя
            CoinService.clear_cache(sender)
            CoinService.clear_cache(recipient)
            logger.debug(f'Транзакция создана: {transaction}')
            return transaction

    @staticmethod
    def clear_cache(user):
        cache_key = f'user_transactions_{user.id}'
        cache.delete(cache_key)

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
        return Transaction.objects.filter(
            models.Q(sender=user) | models.Q(recipient=user)
        )

    @staticmethod
    def get_price_by_category_name(category_name):
        cache_key = f'category_price_{category_name}'
        price = cache.get(cache_key)

        if price is None:
            try:
                price = TransactionCategory.objects.values_list('price', flat=True).get(name=category_name)
                cache.set(cache_key, price, timeout=60 * 15)
            except TransactionCategory.DoesNotExist:
                logger.error(f'Категория не найдена: {category_name}')
                raise ValidationError(__("Категория не найдена"))

        return price
