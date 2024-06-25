from django.db import models
from django.conf import settings

class QRScanHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qr_data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.phone_number} scanned {self.qr_data} on {self.timestamp}'
