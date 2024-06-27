from .models import FriendRequest, Friendship
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from coins.services import CoinService
from django.conf import settings


class FriendService:

    @staticmethod
    def send_friend_request(from_user, to_user):
        # Проверка на существующий запрос
        existing_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user).first()
        if existing_request:
            # Создаем дружбу и удаляем запросы
            FriendService.create_friendship(from_user, to_user)
            existing_request.delete()
            return True, 'Вы теперь друзья!'
        else:
            # Создаем новый запрос
            friend_request = FriendRequest(from_user=from_user, to_user=to_user)
            friend_request.save()
            return False, 'Запрос на добавление в друзья отправлен!'

    @staticmethod
    def confirm_friend_request(friend_request):
        with db_transaction.atomic():
            # Создаем дружбу и удаляем запрос
            FriendService.create_friendship(friend_request.from_user, friend_request.to_user)
            friend_request.delete()
            return 'Запрос в друзья подтвержден!'

    @staticmethod
    def create_friendship(user1, user2):
        with db_transaction.atomic():
            Friendship.objects.create(user1=user1, user2=user2)

            # Определяем количество койнов в зависимости от городов
            if user1.city == user2.city:
                coins = settings.SAME_CITY_FRIEND_REWARD
            else:
                coins = settings.DIFFERENT_CITY_FRIEND_REWARD

            # Создаем транзакции для обновления балансов пользователей
            CoinService.create_transaction(
                sender=user1,
                recipient=user1,
                amount=coins,
                description=f'Reward for adding friend {user2.phone_number}',
                is_system_transaction=True
            )

            CoinService.create_transaction(
                sender=user2,
                recipient=user2,
                amount=coins,
                description=f'Reward for adding friend {user1.phone_number}',
                is_system_transaction=True
            )

            # Удаляем все запросы на дружбу между этими пользователями
            FriendRequest.objects.filter(from_user=user1, to_user=user2).delete()
            FriendRequest.objects.filter(from_user=user2, to_user=user1).delete()

    @staticmethod
    def get_friends(user):
        friendships1 = user.friendships1.all()
        friendships2 = user.friendships2.all()
        friends = [f.user2 for f in friendships1] + [f.user1 for f in friendships2]
        return friends
