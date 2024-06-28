from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from qrcode_generator.utils import generate_qr_code


class Campaign(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    logo = models.ImageField(upload_to='campaigns/logos/', verbose_name=_("Logo"))
    main_photo = models.ImageField(upload_to='campaigns/main_photos/', verbose_name=_("Main Photo"))
    leader_name = models.CharField(max_length=100, verbose_name=_("Leader Name"))
    leader_photo = models.ImageField(upload_to='campaigns/leader_photos/', verbose_name=_("Leader Photo"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    description = models.TextField(verbose_name=_("Description"))
    qr_code = models.ImageField(upload_to='campaigns/qr_codes/', blank=True, null=True, verbose_name=_("QR Code"))

    def __str__(self):
        return self.name

    def generate_qr_code(self):
        qr_data = {"campaign_vote": self.id}
        filebuffer = generate_qr_code(qr_data, f"campaign_{self.id}_vote")
        self.qr_code.save(f"campaign_{self.id}_vote_qr.png", filebuffer, save=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")


class Vote(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='votes', on_delete=models.CASCADE, verbose_name=_("Campaign"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes', on_delete=models.CASCADE,
                             verbose_name=_("User"))
    voted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Voted At"))

    def __str__(self):
        return f'{self.user} voted for {self.campaign}'

    class Meta:
        verbose_name = _("Vote")
        verbose_name_plural = _("Votes")
