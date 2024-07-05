from .models import User
from sms.utils import handle_sms_verification
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.cache import cache

class UserService:

    @staticmethod
    def create_user(phone_number, name, surname, age, city=None, password=None):
        user = User.objects.create_user(
            phone_number=phone_number,
            name=name,
            surname=surname,
            age=age,
            city=city,
            password=password
        )
        return user

    @staticmethod
    def verify_phone_number(phone_number):
        return User.objects.filter(phone_number=phone_number).exists()

    @staticmethod
    def get_user_by_phone_number(phone_number):
        user = cache.get(f'user_{phone_number}')
        if not user:
            user = User.objects.filter(phone_number=phone_number).first()
            cache.set(f'user_{phone_number}', user, timeout=300)
        return user

    @staticmethod
    def handle_sms_verification(request, phone_number):
        handle_sms_verification(request, phone_number)

    @staticmethod
    def is_sms_verification_allowed(request):
        last_sms_time_str = request.session.get('last_sms_time')
        if last_sms_time_str:
            last_sms_time = timezone.make_aware(parse_datetime(last_sms_time_str))
            time_diff = timezone.now() - last_sms_time
            if time_diff.total_seconds() < 60:
                return False, 60 - int(time_diff.total_seconds())
        return True, 0
