from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _, gettext as __
from django.db import transaction
from coins.services import CoinService
from .models import Lecture, LectureAttendance


class LectureService:

    @staticmethod
    def get_lectures():
        return Lecture.objects.all()

    @staticmethod
    def get_lecture_by_id(lecture_id):
        return get_object_or_404(Lecture, id=lecture_id)

    @staticmethod
    def get_attendance(user, lecture):
        return LectureAttendance.objects.filter(user=user, lecture=lecture).first()

    @staticmethod
    @transaction.atomic
    def register_lecture_start(user, lecture):
        attendance, created = LectureAttendance.objects.get_or_create(user=user, lecture=lecture)
        if attendance.start_scanned:
            return False, __('Вы уже отсканировали QR-код начала для этой лекции.')

        attendance.start_scanned = True
        attendance.start_time = timezone.now()
        attendance.save()

        return True, __('Вы успешно зарегистрировались на лекцию.')

    @staticmethod
    @transaction.atomic
    def register_lecture_end(user, lecture):
        attendance = LectureService.get_attendance(user, lecture)
        if not attendance or not attendance.start_scanned:
            return False, __('Сначала нужно отсканировать QR-код начала.')

        if attendance.end_scanned:
            return False, __('Вы уже отсканировали QR-код окончания для этой лекции.')

        attendance.end_scanned = True
        attendance.end_time = timezone.now()
        attendance.save()

        reward_amount = settings.LECTURE_REWARD_COINS
        CoinService.create_transaction(
            sender=user,
            recipient=user,
            amount=reward_amount,
            description=__('Награда за посещение лекции {lecture_title}').format(lecture_title=lecture.title),
            category_name='lecture_bonus'
        )

        return True, __('Вы успешно завершили лекцию и получили {reward_amount} монет.').format(
            reward_amount=reward_amount)
