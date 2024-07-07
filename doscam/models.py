from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
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
    is_published = models.BooleanField(default=False, verbose_name=_("Is Published"))
    is_draft = models.BooleanField(default=True, verbose_name=_("Is Draft"))

    def __str__(self):
        return _("Event between {participant1} and {participant2} at {location}").format(participant1=self.participant1,
                                                                                         participant2=self.participant2,
                                                                                         location=self.location)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.start_time = timezone.now()
            self.end_time = self.start_time + timezone.timedelta(minutes=self.duration_minutes)
        super().save(*args, **kwargs)

    def update_publication_status(self):
        if self.end_time < timezone.now():
            self.is_published = False
            self.save()

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
