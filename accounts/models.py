from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _, gettext as __
from coins.models import DoscointBalance, Transaction
from qrcode_generator.utils import generate_qr_code

class UserManager(BaseUserManager):
    def create_user(self, phone_number, name, surname, age, city=None, password=None):
        if not phone_number:
            raise ValueError(__("Поле 'Номер телефона' обязательно для заполнения"))
        user = self.model(phone_number=phone_number, name=name, surname=surname, age=age, city=city)
        user.set_password(password)
        user.save(using=self._db)
        DoscointBalance.objects.create(user=user, balance=0, total_earned=0)
        return user

    def create_superuser(self, phone_number, name, surname, age, city=None, password=None):
        user = self.create_user(phone_number, name, surname, age, city, password)
        user.is_admin = True
        user.is_superuser = True
        user.is_moderator = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True, verbose_name=_("Номер телефона"))
    name = models.CharField(max_length=30, verbose_name=_("Имя"))
    surname = models.CharField(max_length=30, verbose_name=_("Фамилия"))
    age = models.IntegerField(verbose_name=_("Возраст"))
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Город"))
    instagram = models.CharField(max_length=255, null=True, blank=True, default=' ', verbose_name=_("Instagram"))
    tiktok = models.CharField(max_length=255, null=True, blank=True, default='@', verbose_name=_("TikTok"))
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, verbose_name=_("Фотография профиля"))
    qr_code = models.ImageField(upload_to='profile_pictures/qr_codes/', null=True, blank=True, verbose_name=_("QR-код"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    is_admin = models.BooleanField(default=False, verbose_name=_("Администратор"))
    is_moderator = models.BooleanField(default=False, verbose_name=_("Модератор"))

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name', 'surname', 'age']

    def __str__(self):
        return self.phone_number

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def encrypt_id(self):
        multiplier = settings.ID_MULTIPLIER
        encrypted_id = self.pk * multiplier
        return str(encrypted_id)

    @staticmethod
    def decrypt_id(encrypted_id):
        multiplier = settings.ID_MULTIPLIER
        decrypted_id = int(encrypted_id) // multiplier
        if int(encrypted_id) % multiplier != 0:
            raise ValueError(__("Неверный зашифрованный ID"))
        return decrypted_id

    def generate_qr_code(self):
        qr_data = {"user_id": self.id}
        filebuffer = generate_qr_code(qr_data, f"user_{self.id}_qr")
        self.qr_code.save(f"user_{self.id}_qr.png", filebuffer, save=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()
            super().save(*args, **kwargs)

class City(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Город")
        verbose_name_plural = _("Города")
