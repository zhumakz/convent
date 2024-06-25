import json
from django.conf import settings
from django.db import models
from qrcode_generator.utils import generate_qr_code


class Shop(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchases', on_delete=models.CASCADE, null=True, blank=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sales', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='purchases/qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"Purchase {self.id} by {self.buyer} from {self.seller}"

    def generate_qr_code(self):
        qr_data = {"purchase_id": self.id}
        filebuffer = generate_qr_code(qr_data, f"purchase_{self.id}_qr.png")
        self.qr_code.save(f"purchase_{self.id}_qr.png", filebuffer, save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)
