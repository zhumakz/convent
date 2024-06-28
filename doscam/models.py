from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, gettext as __
import random
from accounts.models import User


class Location(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")


class Event(models.Model):
    participant1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='participant1_events',
                                     on_delete=models.CASCADE, verbose_name=_("Participant 1"))
    participant2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='participant2_events',
                                     on_delete=models.CASCADE, verbose_name=_("Participant 2"))
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name=_("Location"))
    start_time = models.DateTimeField(verbose_name=_("Start Time"))
    end_time = models.DateTimeField(verbose_name=_("End Time"))
    duration_minutes = models.IntegerField(verbose_name=_("Duration Minutes"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Is Completed"))
    participant1_confirmed = models.BooleanField(default=False, verbose_name=_("Participant 1 Confirmed"))
    participant2_confirmed = models.BooleanField(default=False, verbose_name=_("Participant 2 Confirmed"))

    def __str__(self):
        return _("Event between {participant1} and {participant2} at {location}").format(participant1=self.participant1,
                                                                                         participant2=self.participant2,
                                                                                         location=self.location)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.start_time = timezone.now()
            self.end_time = self.start_time + timezone.timedelta(minutes=self.duration_minutes)
        super().save(*args, **kwargs)

    @staticmethod
    def get_random_participants(filters):
        users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
        if filters.get('min_friends'):
            users = users.annotate(friends_count=models.Count('friends')).filter(
                friends_count__gte=filters['min_friends'])
        if filters.get('has_profile_picture'):
            users = users.exclude(profile_picture='')

        if users.count() < 2:
            return None, None

        participants = random.sample(list(users), 2)
        return participants[0], participants[1]

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
