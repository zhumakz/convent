import json
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext as __
from qrcode_generator.utils import generate_qr_code


class Shop(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Owner"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Shop")
        verbose_name_plural = _("Shops")


class Product(models.Model):
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE, verbose_name=_("Shop"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


class Purchase(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchases', on_delete=models.CASCADE, null=True,
                              blank=True, verbose_name=_("Buyer"))
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sales', on_delete=models.CASCADE,
                               verbose_name=_("Seller"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Is Completed"))
    qr_code = models.ImageField(upload_to='purchases/qr_codes/', blank=True, null=True, verbose_name=_("QR Code"))

    def __str__(self):
        return _("Purchase {id} by {buyer} from {seller}").format(id=self.id, buyer=self.buyer, seller=self.seller)

    def generate_qr_code(self):
        qr_data = {"purchase_id": self.id}
        filebuffer = generate_qr_code(qr_data, f"purchase_{self.id}_qr.png")
        self.qr_code.save(f"purchase_{self.id}_qr.png", filebuffer, save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")
