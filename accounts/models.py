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
        user.is_active = False
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
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True,
                                        verbose_name=_("Фотография профиля"))
    qr_code = models.ImageField(upload_to='profile_pictures/qr_codes/', null=True, blank=True, verbose_name=_("QR-код"))
    is_active = models.BooleanField(default=False, verbose_name=_("Активен"))
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

    @staticmethod
    def create_default_city():
        cities_data = [
            {"id": 1, "name_ru": "Астана", "name_kk": "Астана"},
            {"id": 2, "name_ru": "Алматы", "name_kk": "Алматы"},
            {"id": 3, "name_ru": "Актау", "name_kk": "Ақтау"},
            {"id": 4, "name_ru": "Актобе", "name_kk": "Ақтөбе"},
            {"id": 5, "name_ru": "Атырау", "name_kk": "Атырау"},
            {"id": 6, "name_ru": "Жезказган", "name_kk": "Жезқазған"},
            {"id": 7, "name_ru": "Караганда", "name_kk": "Қарағанды"},
            {"id": 8, "name_ru": "Кокшетау", "name_kk": "Көкшетау"},
            {"id": 9, "name_ru": "Конаев", "name_kk": "Қонаев"},
            {"id": 10, "name_ru": "Костанай", "name_kk": "Қостанай"},
            {"id": 11, "name_ru": "Кызылорда", "name_kk": "Қызылорда"},
            {"id": 12, "name_ru": "Павлодар", "name_kk": "Павлодар"},
            {"id": 13, "name_ru": "Петропавловск", "name_kk": "Петропавл"},
            {"id": 14, "name_ru": "Семей", "name_kk": "Семей"},
            {"id": 15, "name_ru": "Талдыкорган", "name_kk": "Талдықорған"},
            {"id": 16, "name_ru": "Тараз", "name_kk": "Тараз"},
            {"id": 17, "name_ru": "Туркестан", "name_kk": "Түркістан"},
            {"id": 18, "name_ru": "Уральск", "name_kk": "Орал"},
            {"id": 19, "name_ru": "Усть-Каменогорск", "name_kk": "Өскемен"},
            {"id": 20, "name_ru": "Шымкент", "name_kk": "Шымкент"}
        ]

        for data in cities_data:
            City.objects.update_or_create(
                id=data['id'],
                defaults={'name_ru': data['name_ru'], 'name_kk': data['name_kk']}
            )
