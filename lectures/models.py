from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _, gettext as __
from qrcode_generator.utils import generate_qr_code


class Lecture(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    speakers = models.CharField(max_length=255, verbose_name=_("Speakers"))
    date = models.DateTimeField(verbose_name=_("Date"))
    location = models.CharField(max_length=255, verbose_name=_("Location"))
    qr_code_start = models.ImageField(upload_to='lectures/qr_codes/start/', blank=True, null=True,
                                      verbose_name=_("QR Code Start"))
    qr_code_end = models.ImageField(upload_to='lectures/qr_codes/end/', blank=True, null=True,
                                    verbose_name=_("QR Code End"))

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
        verbose_name = _("Lecture")
        verbose_name_plural = _("Lectures")


class LectureAttendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, verbose_name=_("Lecture"))
    start_scanned = models.BooleanField(default=False, verbose_name=_("Start Scanned"))
    end_scanned = models.BooleanField(default=False, verbose_name=_("End Scanned"))
    start_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Start Time"))
    end_time = models.DateTimeField(null=True, blank=True, verbose_name=_("End Time"))

    def __str__(self):
        return _('{user} attended {lecture}').format(user=self.user, lecture=self.lecture)

    class Meta:
        verbose_name = _("Lecture Attendance")
        verbose_name_plural = _("Lecture Attendances")
