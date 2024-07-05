from .models import FriendRequest, Friendship
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction, models
from coins.services import CoinService
from django.conf import settings
from django.utils.translation import gettext_lazy as _, gettext as __


class FriendService:

    @staticmethod
    def send_friend_request_common(from_user, to_user, is_qr=False):
        if from_user == to_user:
            error_message = __('You cannot add yourself as a friend.')
            return ('error', error_message) if is_qr else ValidationError(error_message)

        if to_user.is_admin or to_user.is_moderator:
            error_message = __('You cannot add administrators or moderators as friends.')
            return ('error', error_message) if is_qr else ValidationError(error_message)

        existing_request = FriendRequest.objects.filter(
            models.Q(from_user=from_user, to_user=to_user) |
            models.Q(from_user=to_user, to_user=from_user)
        ).first()

        if existing_request:
            if existing_request.from_user == to_user:
                FriendService.create_friendship(from_user, to_user)
                existing_request.delete()
                success_message = __('You are now friends!') if not is_qr else __('Теперь вы друзья!')
                return ('now_friends', success_message) if is_qr else (True, success_message)
            error_message = __('Friend request already sent.') if not is_qr else __(
                'Запрос на добавление в друзья уже отправлен.')
            return ('already_sent', error_message) if is_qr else ValidationError(error_message)

        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()
        success_message = __('Friend request sent!') if not is_qr else __('Запрос на добавление в друзья отправлен!')
        return ('new_request', success_message) if is_qr else (False, success_message)

    @staticmethod
    def send_friend_request(from_user, to_user):
        result, message = FriendService.send_friend_request_common(from_user, to_user, is_qr=False)
        if isinstance(result, ValidationError):
            raise result
        return result, message

    @staticmethod
    def send_friend_requestQR(from_user, to_user):
        return FriendService.send_friend_request_common(from_user, to_user, is_qr=True)

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

            category_name = 'friend_bonus_same_city' if user1.city == user2.city else 'friend_bonus_different_city'

            def create_transaction(user, friend):
                CoinService.create_transaction(
                    sender=user,
                    recipient=user,
                    description=__('Reward for adding friend {phone_number}').format(phone_number=friend.phone_number),
                    category_name=category_name
                )

            create_transaction(user1, user2)
            create_transaction(user2, user1)

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
