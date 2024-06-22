from django.db import models
from django.conf import settings
from io import BytesIO
from django.core.files import File
import qrcode
import json

class Shop(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='shops', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Purchase(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sales', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchases', on_delete=models.CASCADE, null=True, blank=True)
    shop = models.ForeignKey(Shop, related_name='purchases', on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='purchases/qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"{self.seller} -> {self.buyer} : {self.amount}"

    def generate_qr_code(self):
        qr_data = json.dumps({
            "purchase_id": self.id
        })
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        buffer = BytesIO()
        img.save(buffer)
        filename = f"purchase_{self.id}_qr.png"
        filebuffer = File(buffer, name=filename)
        self.qr_code.save(filename, filebuffer)
        self.save()
