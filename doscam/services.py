from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import transaction as db_transaction
from django.utils.translation import gettext_lazy as _, gettext as __
from .models import Event
from accounts.models import User
from coins.services import CoinService
from friends.services import FriendService
import random
import logging

logger = logging.getLogger(__name__)

class EventService:

    @staticmethod
    def create_event(location, duration_minutes, min_friends, has_profile_picture, publish=False):
        filters = {
            'min_friends': min_friends,
            'has_profile_picture': has_profile_picture
        }
        participant1, participant2 = Event.get_random_participants(filters)

        if not participant1 or not participant2:
            logger.warning("Not enough participants meet the criteria.")
            return None, __("Not enough participants meet the criteria.")

        if publish:
            Event.objects.filter(is_published=True, is_completed=False).update(is_published=False)

        event = Event.objects.create(
            participant1=participant1,
            participant2=participant2,
            location=location,
            duration_minutes=duration_minutes,
            is_published=publish,
            is_draft=not publish
        )
        return event, None

    @staticmethod
    def confirm_participation(user, event):
        if event.participant1 == user:
            event.participant1_confirmed = True
        elif event.participant2 == user:
            event.participant2_confirmed = True
        else:
            logger.error(f"User {user} is not a participant of the event {event}.")
            raise ValidationError(__("User is not a participant of the event."))

        event.save()

        if event.participant1_confirmed and event.participant2_confirmed:
            EventService.complete_event(event)
            return True, __("Event completed successfully!")
        else:
            return False, __("Waiting for the other participant to confirm.")

    @staticmethod
    @db_transaction.atomic
    def complete_event(event):
        event.is_completed = True
        event.save()
        reward_amount = settings.DOSCAM_EVENT_REWARD

        # Создаем транзакции с использованием CoinService
        CoinService.create_transaction(
            sender=event.participant1,
            recipient=event.participant1,
            amount=reward_amount,
            description=__('Reward for completing Doscam event with {participant}').format(participant=event.participant2),
            is_system_transaction=True
        )
        CoinService.create_transaction(
            sender=event.participant2,
            recipient=event.participant2,
            amount=reward_amount,
            description=__('Reward for completing Doscam event with {participant}').format(participant=event.participant1),
            is_system_transaction=True
        )

        # Добавляем пользователей в друзья через приложение friends
        if not FriendService.are_friends(event.participant1, event.participant2):
            FriendService.create_friendship(event.participant1, event.participant2)

        # Снимаем публикацию события после завершения
        event.is_published = False
        event.save()
