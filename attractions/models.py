from django.db import models
from django.utils.translation import gettext_lazy as _


class Attraction(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Название"))
    description = models.TextField(null=True, blank=True, default=' ', verbose_name=_("Описание"))
    photo = models.ImageField(upload_to='attractions/photos/', null=True, blank=True, verbose_name=_("Фото"))
    start_time = models.DateTimeField(verbose_name=_("Время начала"))
    end_time = models.DateTimeField(verbose_name=_("Время окончания"))
    location = models.CharField(max_length=255, verbose_name=_("Местоположение"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Аттракцион")
        verbose_name_plural = _("Аттракционы")
