from django.db import models
from django.utils.translation import gettext_lazy as _

class StaticPage(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    photo = models.ImageField(upload_to='static_pages/photos/', verbose_name=_('Photo'), blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Static Page')
        verbose_name_plural = _('Static Pages')
