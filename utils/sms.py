import requests
from django.conf import settings

def send_sms(phone_number, message):
    if settings.SMSC_TEST_MODE:
        print(f"Test SMS to {phone_number}: {message}")
        return True

    params = {
        'login': settings.SMSC_LOGIN,
        'psw': settings.SMSC_PASSWORD,
        'phones': phone_number,
        'mes': message,
        'test': 1 if settings.SMSC_TEST_MODE else 0,
        'fmt': 3  # JSON response format
    }

    response = requests.get(settings.SMSC_URL, params=params)

    if response.status_code == 200:
        result = response.json()
        if "error" in result:
            print(f"Error sending SMS: {result['error']}")
            return False
        return True
    else:
        print(f"HTTP error: {response.status_code}")
        return False
