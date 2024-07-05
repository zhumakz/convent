from .models import FriendRequest, Friendship
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from coins.services import CoinService
from django.conf import settings
from django.utils.translation import gettext_lazy as _, gettext as __


class FriendService:

    @staticmethod
    def send_friend_request(from_user, to_user):
        # Проверка на попытку добавления самого себя
        if from_user == to_user:
            raise ValidationError(__('You cannot add yourself as a friend.'))

        # Проверка на попытку добавления администратора или модератора
        if to_user.is_admin or to_user.is_moderator:
            raise ValidationError(__('You cannot add administrators or moderators as friends.'))

        # Проверка на существующий запрос от получателя к отправителю
        existing_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user).first()
        if existing_request:
            # Создаем дружбу и удаляем запросы
            FriendService.create_friendship(from_user, to_user)
            existing_request.delete()
            return True, __('You are now friends!')

        # Проверка на существующий запрос от отправителя к получателю
        existing_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).first()
        if existing_request:
            raise ValidationError(__('Friend request already sent.'))

        # Создаем новый запрос
        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()
        return False, __('Friend request sent!')

    @staticmethod
    def send_friend_requestQR(from_user, to_user):
        # Проверка на попытку добавления самого себя
        if from_user == to_user:
            return 'error', __('Вы не можете добавить себя в друзья.')

        # Проверка на попытку добавления администратора или модератора
        if to_user.is_admin or to_user.is_moderator:
            return 'error', __('Вы не можете добавить в друзья администраторов или модераторов.')

        # Проверка на существующий запрос от получателя к отправителю
        existing_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user).first()
        if existing_request:
            # Создаем дружбу и удаляем запросы
            FriendService.create_friendship(from_user, to_user)
            existing_request.delete()
            return 'now_friends', __('Теперь вы друзья!')

        # Проверка на существующий запрос от отправителя к получателю
        existing_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).first()
        if existing_request:
            return 'already_sent', __('Запрос на добавление в друзья уже отправлен.')

        # Создаем новый запрос
        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()
        return 'new_request', __('Запрос на добавление в друзья отправлен!')

    @staticmethod
    def confirm_friend_request(friend_request):
        with db_transaction.atomic():
            # Создаем дружбу и удаляем запрос
            FriendService.create_friendship(friend_request.from_user, friend_request.to_user)
            friend_request.delete()
            return __('Friend request confirmed!')

    @staticmethod
    def create_friendship(user1, user2):
        with db_transaction.atomic():
            Friendship.objects.create(user1=user1, user2=user2)

            # Определяем категорию транзакции в зависимости от городов пользователей
            if user1.city == user2.city:
                category_name = 'friend_bonus_same_city'
            else:
                category_name = 'friend_bonus_different_city'

            # Создаем транзакции для обоих пользователей
            CoinService.create_transaction(
                sender=user1,
                recipient=user1,
                description=__('Reward for adding friend {phone_number}').format(phone_number=user2.phone_number),
                category_name=category_name
            )

            CoinService.create_transaction(
                sender=user2,
                recipient=user2,
                description=__('Reward for adding friend {phone_number}').format(phone_number=user1.phone_number),
                category_name=category_name
            )

            # Удаляем все запросы на дружбу между этими пользователями
            FriendRequest.objects.filter(from_user=user1, to_user=user2).delete()
            FriendRequest.objects.filter(from_user=user2, to_user=user1).delete()

    @staticmethod
    def get_friends(user):
        friendships1 = user.friendships1.select_related('user2__city').all()
        friendships2 = user.friendships2.select_related('user1__city').all()
        friends = [f.user2 for f in friendships1] + [f.user1 for f in friendships2]
        return friends

    @staticmethod
    def are_friends(user1, user2):
        return Friendship.objects.filter(user1=user1, user2=user2).exists() or Friendship.objects.filter(user1=user2,
                                                                                                         user2=user1).exists()
