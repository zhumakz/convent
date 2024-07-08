# badges/models.py
from django.db import models
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from django.core.files.base import ContentFile


class Badge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='badges/')

    def create_badge(self):
        user = self.user

        # Загрузка фоновой картинки
        background_path = os.path.join(settings.BASE_DIR, 'static/image/badge/background.png')
        background = Image.open(background_path)
        background = background.resize((1353, 1950))

        draw = ImageDraw.Draw(background)
        font = ImageFont.load_default()

        # Загрузка шрифта с указанием размера
        font_path = os.path.join(settings.BASE_DIR, 'static/fonts/SF/SFProDisplay-Bold.ttf')
        font_size = 130  # Укажите размер шрифта
        font = ImageFont.truetype(font_path, font_size)

        # Размещение имени, фамилии и города
        draw.text((450, 610), f'{user.name}', font=font, fill="red", align="center")
        draw.text((450, 735), f'{user.surname}', font=font, fill="red", align="center")
        if user.city:
            draw.text((450, 900), f'{user.city.name}', font=font, fill="red", align="center")

        # Добавление QR-кода
        if user.qr_code:
            qr_code_path = user.qr_code.path
            qr_code = Image.open(qr_code_path)
            qr_code = qr_code.resize((600, 600))  # Измените размер QR-кода при необходимости SFProDisplay-Semibold.ttf
            background.paste(qr_code, (375, 1205))  # Координаты, где разместить QR-код на бейдже

        badge_directory = os.path.join(settings.MEDIA_ROOT, 'badges')
        if not os.path.exists(badge_directory):
            os.makedirs(badge_directory)

        badge_filename = f'{user.phone_number}_badge.png'
        badge_path = os.path.join(badge_directory, badge_filename)

        # Сохраняем изображение во временный буфер
        buffer = BytesIO()
        background.save(buffer, format='PNG')
        buffer.seek(0)

        # Сохраняем изображение в поле image модели Badge
        self.image.save(badge_filename, ContentFile(buffer.read()), save=False)
        self.save()
