from django.db import models
from django.utils.translation import gettext_lazy as _


class Attraction(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(null=True, blank=True, default=' ', verbose_name=_("Description"))
    photo = models.ImageField(upload_to='attractions/photos/', null=True, blank=True, verbose_name=_("Photo"))
    start_time = models.DateTimeField(verbose_name=_("Start Time"))
    end_time = models.DateTimeField(verbose_name=_("End Time"))
    location = models.CharField(max_length=255, verbose_name=_("Location"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Расписание")
        verbose_name_plural = _("Расписание")
