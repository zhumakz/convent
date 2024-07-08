from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import random
from accounts.models import User


class Location(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название"))
    address = models.CharField(max_length=255, verbose_name=_("Адрес"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Местоположение")
        verbose_name_plural = _("Местоположения")

    @staticmethod
    def create_default_locations():
        locations_data = [
            {"id": 1, "name": "DosCam «Креатив»", "address": "DosCam «Креатив»"},
            {"id": 2, "name": "DosCam «Энергия»", "address": "DosCam «Қуат»"},
            {"id": 3, "name": "DosCam «Мышление»", "address": "DosCam «Сана»"}
        ]

        for data in locations_data:
            Location.objects.update_or_create(
                id=data['id'],
                defaults={'name': data['name'], 'address': data['address']}
            )


class Event(models.Model):
    participant1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='participant1_events',
                                     on_delete=models.CASCADE, verbose_name=_("Участник 1"))
    participant2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='participant2_events',
                                     on_delete=models.CASCADE, verbose_name=_("Участник 2"))
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name=_("Местоположение"))
    start_time = models.DateTimeField(verbose_name=_("Время начала"))
    end_time = models.DateTimeField(verbose_name=_("Время окончания"))
    duration_minutes = models.IntegerField(verbose_name=_("Продолжительность (минуты)"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Завершено"))
    participant1_confirmed = models.BooleanField(default=False, verbose_name=_("Участник 1 подтвердил"))
    participant2_confirmed = models.BooleanField(default=False, verbose_name=_("Участник 2 подтвердил"))
    is_published = models.BooleanField(default=False, verbose_name=_("Опубликовано"))
    is_draft = models.BooleanField(default=True, verbose_name=_("Черновик"))

    def __str__(self):
        return _("Событие между {participant1} и {participant2} в {location}").format(
            participant1=self.participant1,
            participant2=self.participant2,
            location=self.location
        )

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
        verbose_name = _("Событие")
        verbose_name_plural = _("События")
