from django.db import models
from django.conf import settings
from qrcode_generator.utils import generate_qr_code
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
        qr_data = {"lecture_start": self.id}
        filebuffer = generate_qr_code(qr_data, f"lecture_{self.id}_start_qr")
        self.qr_code_start.save(f"lecture_{self.id}_start_qr.png", filebuffer, save=False)

    def generate_qr_code_end(self):
        qr_data = {"lecture_end": self.id}
        filebuffer = generate_qr_code(qr_data, f"lecture_{self.id}_end_qr")
        self.qr_code_end.save(f"lecture_{self.id}_end_qr.png", filebuffer, save=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code_start or not self.qr_code_end:
            self.generate_qr_code_start()
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
