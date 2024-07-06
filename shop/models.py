import json
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext as __
from qrcode_generator.utils import generate_qr_code


class Shop(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Владелец"))
    address = models.CharField(max_length=255, verbose_name=_("Адрес"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")


class Product(models.Model):
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE, verbose_name=_("Магазин"))
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(verbose_name=_("Описание"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")


class Purchase(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchases', on_delete=models.CASCADE, null=True,
                              blank=True, verbose_name=_("Покупатель"))
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sales', on_delete=models.CASCADE,
                               verbose_name=_("Продавец"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Сумма"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Завершено"))
    is_cancelled = models.BooleanField(default=False, verbose_name=_("Отменено"))
    qr_code = models.ImageField(upload_to='purchases/qr_codes/', blank=True, null=True, verbose_name=_("QR-код"))

    def __str__(self):
        return _("Покупка {id} от {buyer} у {seller}").format(id=self.id, buyer=self.buyer, seller=self.seller)

    def generate_qr_code(self):
        qr_data = {"purchase_id": self.id}
        filebuffer = generate_qr_code(qr_data, f"purchase_{self.id}_qr.png")
        self.qr_code.save(f"purchase_{self.id}_qr.png", filebuffer, save=False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.generate_qr_code()
            super().save(update_fields=['qr_code'])

    class Meta:
        verbose_name = _("Покупка")
        verbose_name_plural = _("Покупки")
