from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import transaction as db_transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, gettext as __
from .models import Event, Location
from accounts.models import User
from coins.services import CoinService
from friends.services import FriendService
import random
import logging

logger = logging.getLogger(__name__)

class EventService:
    @staticmethod
    def create_event_with_params(participant1, participant2, location, duration_minutes, has_profile_picture, publish=False):
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
    def get_random_participants_and_location(has_profile_picture=False):
        users = User.objects.filter(is_active=True, is_moderator=False, is_superuser=False)

        if has_profile_picture:
            users = users.exclude(profile_picture='')

        users = list(users)
        if len(users) < 2:
            return None, None, None

        participants = random.sample(users, 2)
        location = EventService.get_random_location()

        if not location:
            return None, None, None

        return participants[0], participants[1], location

    @staticmethod
    def get_random_location():
        locations = list(Location.objects.all())
        if not locations:
            return None
        return random.choice(locations)

    @staticmethod
    def check_active_event():
        now = timezone.now()
        active_event = Event.objects.filter(is_published=True, is_completed=False, end_time__gt=now).first()
        return active_event

    @staticmethod
    def check_active_event_by_user(user):
        now = timezone.now()
        active_event = Event.objects.filter(
            (Q(participant1=user) | Q(participant2=user)) &
            Q(is_published=True) &
            Q(is_completed=False) &
            Q(end_time__gt=now)
        ).first()
        return active_event

    @staticmethod
    def get_ready_participants_count():
        return User.objects.filter(is_active=True, is_moderator=False, is_superuser=False).exclude(
            profile_picture='').count()

    @staticmethod
    def confirm_participation(user, event):
        if event.participant1 == user:
            event.participant1_confirmed = True
        elif event.participant2 == user:
            event.participant2_confirmed = True
        else:
            logger.error(f"Пользователь {user} не является участником события {event}.")
            raise ValidationError(__("Пользователь не является участником события."))

        event.save()

        if event.participant1_confirmed and event.participant2_confirmed:
            EventService.complete_event(event)
            return True, __("Событие успешно завершено!")
        else:
            return False, __("Ожидание подтверждения от другого участника.")

    @staticmethod
    @db_transaction.atomic
    def complete_event(event):
        event.is_completed = True
        event.save()
        reward_amount = settings.DOSCAM_EVENT_REWARD

        CoinService.create_transaction(
            sender=event.participant1,
            recipient=event.participant1,
            amount=reward_amount,
            description=__('Награда за завершение события Doscam с {participant}').format(participant=event.participant2),
            category_name='event_bonus'
        )
        CoinService.create_transaction(
            sender=event.participant2,
            recipient=event.participant2,
            amount=reward_amount,
            description=__('Награда за завершение события Doscam с {participant}').format(participant=event.participant1),
            category_name='event_bonus'
        )

        if not FriendService.are_friends(event.participant1, event.participant2):
            FriendService.create_friendship(event.participant1, event.participant2)

        event.is_published = False
        event.save()
