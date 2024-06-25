from django.db import models
from django.conf import settings
from qrcode_generator.utils import generate_qr_code


class Shop(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchases', on_delete=models.CASCADE, null=True,
                              blank=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sales', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='purchases', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='purchases/qr_codes/', blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f'Purchase of {self.product.name if self.product else "Custom Amount"} by {self.buyer}'

    def generate_qr_code(self):
        qr_data = {"purchase_id": self.id}
        qr_file, qr_filename = generate_qr_code(qr_data, f"purchase_{self.id}")
        self.qr_code.save(qr_filename, qr_file, save=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()
            super().save(*args, **kwargs)
