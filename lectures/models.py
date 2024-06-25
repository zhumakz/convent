from django.db import models
from django.conf import settings
from qrcode_generator.utils import generate_qr_code

class Lecture(models.Model):
    title = models.CharField(max_length=255)
    speakers = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    qr_code_start = models.ImageField(upload_to='lectures/qr_codes/start/', blank=True, null=True)
    qr_code_end = models.ImageField(upload_to='lectures/qr_codes/end/', blank=True, null=True)

    def __str__(self):
        return self.title

    def generate_qr_codes(self):
        start_qr_data = {"lecture_start": self.id}
        end_qr_data = {"lecture_end": self.id}

        start_qr_file, start_qr_filename = generate_qr_code(start_qr_data, f"lecture_{self.id}_start")
        end_qr_file, end_qr_filename = generate_qr_code(end_qr_data, f"lecture_{self.id}_end")

        self.qr_code_start.save(start_qr_filename, start_qr_file, save=False)
        self.qr_code_end.save(end_qr_filename, end_qr_file, save=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code_start or not self.qr_code_end:
            self.generate_qr_codes()
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
