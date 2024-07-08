from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from coins.models import DoscointBalance, Transaction
from coins.services import CoinService
from django.contrib.auth.models import Group

User = get_user_model()

class CoinServiceTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(phone_number='+77470000001', name='User', surname='One', age=30, password='password')
        self.user2 = User.objects.create_user(phone_number='+77470000002', name='User', surname='Two', age=25, password='password')

        # Создаем баланс для пользователей
        DoscointBalance.objects.create(user=self.user1, balance=100)
        DoscointBalance.objects.create(user=self.user2, balance=50)

    def test_create_transaction(self):
        # Проверяем создание транзакции
        transaction = CoinService.create_transaction(
            sender=self.user1,
            recipient=self.user2,
            amount=10,
            description='Test Transaction'
        )

        self.assertEqual(transaction.amount, 10)
        self.assertEqual(transaction.sender, self.user1)
        self.assertEqual(transaction.recipient, self.user2)

        # Проверяем обновление балансов
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.doscointbalance.balance, 90)
        self.assertEqual(self.user2.doscointbalance.balance, 60)

    def test_create_transaction_insufficient_balance(self):
        # Проверяем создание транзакции при недостаточном балансе
        with self.assertRaises(ValidationError):
            CoinService.create_transaction(
                sender=self.user2,
                recipient=self.user1,
                amount=60,
                description='Test Insufficient Balance'
            )

    def test_create_transaction_negative_amount(self):
        # Проверяем создание транзакции с отрицательной суммой
        with self.assertRaises(ValidationError):
            CoinService.create_transaction(
                sender=self.user1,
                recipient=self.user2,
                amount=-10,
                description='Test Negative Amount'
            )

    def test_add_coins_moderator(self):
        # Добавляем пользователя в группу AddModerators
        self.user1.groups.add(self.add_moderators_group)

        # Проверяем создание транзакции модератором AddModerators с суммой больше 10
        with self.assertRaises(ValidationError):
            CoinService.create_transaction(
                sender=self.user1,
                recipient=self.user2,
                amount=20,
                description='Test AddModerators Limit'
            )

    def test_remove_coins_moderator(self):
        # Добавляем пользователя в группу RemoveModerators
        self.user2.groups.add(self.remove_moderators_group)

        # Проверяем создание транзакции модератором RemoveModerators с суммой, которая уменьшит баланс до
        # отрицательного значения
        with self.assertRaises(ValidationError):
            CoinService.create_transaction(
                sender=self.user1,
                recipient=self.user2,
                amount=60,
                description='Test RemoveModerators Limit'
            )


class CoinViewsTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(phone_number='+77470000001', name='User', surname='One', age=30, password='password')
        self.user2 = User.objects.create_user(phone_number='+77470000002', name='User', surname='Two', age=25, password='password')

        # Создаем баланс для пользователей
        DoscointBalance.objects.create(user=self.user1, balance=100)
        DoscointBalance.objects.create(user=self.user2, balance=50)

        self.client.login(phone_number='+77470000001', password='password')

    def test_balance_view(self):
        response = self.client.get(reverse('balance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Current Balance: 100 coins')

    def test_add_coins_view(self):
        response = self.client.post(reverse('add_coins'), {
            'recipient': self.user2.id,
            'amount': 10,
            'description': 'Test Add Coins'
        })
        self.assertEqual(response.status_code, 302)
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.doscointbalance.balance, 90)
        self.assertEqual(self.user2.doscointbalance.balance, 60)

    def test_remove_coins_view(self):
        response = self.client.post(reverse('remove_coins'), {
            'recipient': self.user2.id,
            'amount': 10,
            'description': 'Test Remove Coins'
        })
        self.assertEqual(response.status_code, 302)
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.doscointbalance.balance, 90)
        self.assertEqual(self.user2.doscointbalance.balance, 40)

    def test_add_coins_view_insufficient_balance(self):
        response = self.client.post(reverse('add_coins'), {
            'recipient': self.user2.id,
            'amount': 110,
            'description': 'Test Add Coins Insufficient Balance'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Insufficient balance')

    def test_remove_coins_view_insufficient_balance(self):
        response = self.client.post(reverse('remove_coins'), {
            'recipient': self.user2.id,
            'amount': 60,
            'description': 'Test Remove Coins Insufficient Balance'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'RemoveModerators cannot reduce balance below 0')
