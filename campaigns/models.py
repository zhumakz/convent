from django.db import models
from django.conf import settings
from qrcode_generator.utils import generate_qr_code

class Campaign(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='campaigns/logos/')
    main_photo = models.ImageField(upload_to='campaigns/main_photos/')
    leader_name = models.CharField(max_length=100)
    leader_photo = models.ImageField(upload_to='campaigns/leader_photos/')
    city = models.CharField(max_length=100)
    description = models.TextField()
    qr_code = models.ImageField(upload_to='campaigns/qr_codes/', blank=True, null=True)

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


class Vote(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='votes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes', on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} voted for {self.campaign}'
