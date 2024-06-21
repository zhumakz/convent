from django.db import models
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File
import json

class Lecture(models.Model):
    title = models.CharField(max_length=255)
    speakers = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    qr_code_start = models.ImageField(upload_to='lectures/qr_codes/start/', blank=True, null=True)
    qr_code_end = models.ImageField(upload_to='lectures/qr_codes/end/', blank=True, null=True)

    def __str__(self):
        return self.title

    def generate_qr_code_start(self):
        qr_data = json.dumps({"lecture_start": self.id})
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
        img.save(buffer, format="PNG")
        self.qr_code_start.save(f"lecture_{self.id}_start_qr.png", File(buffer), save=False)
        buffer.close()

    def generate_qr_code_end(self):
        qr_data = json.dumps({"lecture_end": self.id})
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
        img.save(buffer, format="PNG")
        self.qr_code_end.save(f"lecture_{self.id}_end_qr.png", File(buffer), save=False)
        buffer.close()

    def save(self, *args, **kwargs):
        if not self.qr_code_start:
            self.generate_qr_code_start()
        if not self.qr_code_end:
            self.generate_qr_code_end()
        super().save(*args, **kwargs)

class LectureAttendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    start_scanned = models.BooleanField(default=False)
    end_scanned = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} attended {self.lecture}'
