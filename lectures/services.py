from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from coins.services import CoinService
from .models import Lecture, LectureAttendance
from accounts.models import User

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
    def register_lecture_start(user, lecture):
        attendance, created = LectureAttendance.objects.get_or_create(user=user, lecture=lecture)
        if attendance.start_scanned:
            return False, 'You have already scanned the start QR code for this lecture.'

        attendance.start_scanned = True
        attendance.start_time = timezone.now()
        attendance.save()

        return True, 'You have successfully registered for the lecture.'

    @staticmethod
    def register_lecture_end(user, lecture):
        attendance = LectureService.get_attendance(user, lecture)
        if not attendance or not attendance.start_scanned:
            return False, 'You need to scan the start QR code first.'

        if attendance.end_scanned:
            return False, 'You have already scanned the end QR code for this lecture.'

        attendance.end_scanned = True
        attendance.end_time = timezone.now()
        attendance.save()

        reward_amount = settings.LECTURE_REWARD_COINS
        CoinService.create_transaction(
            sender=user,
            recipient=user,
            amount=reward_amount,
            description=f'Reward for attending lecture {lecture.title}',
            is_system_transaction=True
        )

        return True, f'You have successfully completed the lecture and received {reward_amount} coins.'
