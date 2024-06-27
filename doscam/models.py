from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import User
from coins.models import Transaction
from friends.models import FriendRequest, Friendship
import random

class Location(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Event(models.Model):
    participant1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='participant1_events', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='participant2_events', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    participant1_confirmed = models.BooleanField(default=False)
    participant2_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Event between {self.participant1} and {self.participant2} at {self.location}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.start_time = timezone.now()
            self.end_time = self.start_time + timezone.timedelta(minutes=self.duration_minutes)
        super().save(*args, **kwargs)

    def complete_event(self):
        self.is_completed = True
        self.save()
        reward_amount = settings.DOSCAM_EVENT_REWARD

        # Создаем транзакции
        Transaction.objects.create(
            sender=self.participant1,
            recipient=self.participant1,
            amount=reward_amount,
            description=f"Reward for completing Doscam event with {self.participant2}",
            is_system_transaction=True
        )
        Transaction.objects.create(
            sender=self.participant2,
            recipient=self.participant2,
            amount=reward_amount,
            description=f"Reward for completing Doscam event with {self.participant1}",
            is_system_transaction=True
        )

        # Добавляем пользователей в друзья через приложение friends
        if not Friendship.objects.filter(user1=self.participant1, user2=self.participant2).exists() and \
           not Friendship.objects.filter(user1=self.participant2, user2=self.participant1).exists():
            if FriendRequest.objects.filter(from_user=self.participant1, to_user=self.participant2).exists():
                friend_request = FriendRequest.objects.get(from_user=self.participant1, to_user=self.participant2)
                friend_request.accept()
            elif FriendRequest.objects.filter(from_user=self.participant2, to_user=self.participant1).exists():
                friend_request = FriendRequest.objects.get(from_user=self.participant2, to_user=self.participant1)
                friend_request.accept()
            else:
                FriendRequest.objects.create(from_user=self.participant1, to_user=self.participant2)

    @staticmethod
    def get_random_participants(filters):
        users = User.objects.all()
        if filters.get('min_friends'):
            users = users.annotate(friends_count=models.Count('friends')).filter(friends_count__gte=filters['min_friends'])
        if filters.get('has_profile_picture'):
            users = users.exclude(profile_picture='')

        if users.count() < 2:
            return None, None

        participants = random.sample(list(users), 2)
        return participants[0], participants[1]