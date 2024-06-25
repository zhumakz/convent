import requests
from django.conf import settings
from django.utils import timezone
from django.utils.dateformat import format
import random

def generate_sms_code():
    return str(random.randint(1000, 9999))

def send_sms(phone_number, message):
    if settings.SMSC_TEST_MODE:
        # Вывод в консоль в тестовом режиме
        print(f"Sending SMS to {phone_number}: {message}")
        return True

    payload = {
        'login': settings.SMSC_LOGIN,
        'psw': settings.SMSC_PASSWORD,
        'phones': phone_number,
        'mes': message,
        'sender': 'SMS',
        'fmt': 3,
        'charset': 'utf-8',
        'test': int(settings.SMSC_TEST_MODE),
    }
    response = requests.get(settings.SMSC_URL, params=payload)
    if response.status_code == 200:
        response_data = response.json()
        print(f"SMS API response: {response_data}")  # Вывод ответа API для отладки
        return response_data.get('error', 0) == 0
    else:
        print(f"Failed to send SMS, status code: {response.status_code}")
        return False

def handle_sms_verification(request, phone_number):
    sms_code = generate_sms_code()
    request.session['phone_number'] = phone_number
    request.session['sms_code'] = sms_code
    request.session['sms_sent'] = True
    request.session['last_sms_time'] = format(timezone.now(), 'Y-m-d H:i:s')
    message = f"{settings.SMS_VERIFICATION_MESSAGE} {sms_code}"
    send_sms(phone_number, message)
    return sms_code
