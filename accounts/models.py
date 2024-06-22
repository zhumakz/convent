from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files import File
import qrcode
import io

from django.db.models.signals import post_save
from django.dispatch import receiver
from coins.models import DoscointBalance, Transaction


class UserManager(BaseUserManager):
    def create_user(self, phone_number, name, surname, age, city=None, password=None):
        if not phone_number:
            raise ValueError("The Phone Number field is required")
        user = self.model(phone_number=phone_number, name=name, surname=surname, age=age, city=city)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, surname, age, city=None, password=None):
        user = self.create_user(phone_number, name, surname, age, city, password)
        user.is_admin = True
        user.is_superuser = True
        user.is_moderator = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    age = models.IntegerField()
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)

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
        if int(encrypted_id) % multiplier != 0:  # Check if valid multiplication
            raise ValueError("Invalid encrypted ID")
        return decrypted_id

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = self.encrypt_id()
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        file_name = f'{self.phone_number}_qr.png'
        self.qr_code.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Сначала сохраняем пользователя, чтобы получить его pk
        if not self.qr_code:
            self.generate_qr_code()
            super().save(*args, **kwargs)  # Сохраняем снова, чтобы сохранить QR-код


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        balance, _ = DoscointBalance.objects.get_or_create(user=instance)
        Transaction.objects.create(
            sender=instance,
            recipient=instance,
            amount=0,
            description="Initial balance creation",
            is_system_transaction=True
        )
