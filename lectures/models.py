from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _, gettext as __
from qrcode_generator.utils import generate_qr_code


class Lecture(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Название"))
    speakers = models.CharField(max_length=255, verbose_name=_("Спикеры"))
    date = models.DateTimeField(verbose_name=_("Дата"))
    location = models.CharField(max_length=255, verbose_name=_("Место проведения"))
    qr_code_start = models.ImageField(upload_to='lectures/qr_codes/start/', blank=True, null=True, verbose_name=_("QR-код начала"))
    qr_code_end = models.ImageField(upload_to='lectures/qr_codes/end/', blank=True, null=True, verbose_name=_("QR-код окончания"))

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

    class Meta:
        verbose_name = _("Лекция")
        verbose_name_plural = _("Лекции")


class LectureAttendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, verbose_name=_("Лекция"))
    start_scanned = models.BooleanField(default=False, verbose_name=_("Начало отсканировано"))
    end_scanned = models.BooleanField(default=False, verbose_name=_("Окончание отсканировано"))
    start_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Время начала"))
    end_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Время окончания"))

    def __str__(self):
        return _('{user} посетил {lecture}').format(user=self.user, lecture=self.lecture)

    class Meta:
        verbose_name = _("Посещение лекции")
        verbose_name_plural = _("Посещения лекций")
