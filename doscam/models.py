from django.db import models
from django.conf import settings
from django.utils import timezone
from coins.models import Transaction

class Event(models.Model):
    participant1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='events_as_participant1', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='events_as_participant2', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Event between {self.participant1} and {self.participant2} at {self.location}"

    def is_active(self):
        return not self.is_completed and self.start_time <= timezone.now() <= self.end_time

    def complete_event(self):
        self.is_completed = True
        self.save()

        reward_amount = settings.DOSCAM_EVENT_REWARD
        Transaction.objects.create(
            sender=self.participant1,
            recipient=self.participant1,
            amount=reward_amount,
            description=f'Reward for completing event with {self.participant2}',
            is_system_transaction=True
        )
        Transaction.objects.create(
            sender=self.participant2,
            recipient=self.participant2,
            amount=reward_amount,
            description=f'Reward for completing event with {self.participant1}',
            is_system_transaction=True
        )
