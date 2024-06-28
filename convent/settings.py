import os
from pathlib import Path
import environ

# Инициализация библиотеки environ
env = environ.Env(
    # задать casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'friends',
    'coins',
    'main',
    'qrcode_generator',
    'campaigns',
    'leaderboard',
    'lectures',
    'shop',
    'sms',
    'qr_handler',
    'doscam',
    'attractions',
    'static_pages',
    'debug_toolbar',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'convent.middleware.BaseTemplateMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'convent.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'coins.context_processors.add_balance_to_context',
                'convent.context_processors.base_template',
            ],
        },
    },
]

WSGI_APPLICATION = 'convent.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUTHENTICATION_BACKENDS = [
    'accounts.backends.PhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'accounts.User'

# Настройки для SMSC.kz
SMSC_LOGIN = env('SMSC_LOGIN')
SMSC_PASSWORD = env('SMSC_PASSWORD')
SMSC_TEST_MODE = env.bool('SMSC_TEST_MODE', default=True)  # False для боевого режима
SMSC_URL = 'https://smsc.kz/sys/send.php'
SMS_VERIFICATION_MESSAGE = "Код для авторизации Жаңа адамдар:"

QR_CODE_KEY = env.bytes('QR_CODE_KEY')
ID_MULTIPLIER = env.int('ID_MULTIPLIER', default=37)
ENCRYPTION_METHOD = env('ENCRYPTION_METHOD', default='simple')  # 'simple' или 'cryptography'

COINS_SAME_CITY = env.int('COINS_SAME_CITY', default=1)
COINS_DIFFERENT_CITY = env.int('COINS_DIFFERENT_CITY', default=2)

# Вознаграждение за добавление в друзья
SAME_CITY_FRIEND_REWARD = env.int('SAME_CITY_FRIEND_REWARD', default=1)
DIFFERENT_CITY_FRIEND_REWARD = env.int('DIFFERENT_CITY_FRIEND_REWARD', default=2)
LECTURE_REWARD_COINS = env.int('LECTURE_REWARD_COINS', default=5)
VOTE_REWARD_COINS = env.int('VOTE_REWARD_COINS', default=5)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

DOSCAM_EVENT_REWARD = 50

DEBUG_TOOLBAR_CONFIG = {}
DEBUG_TOOLBAR_CONFIG['IS_RUNNING_TESTS'] = False

INTERNAL_IPS = [
    '127.0.0.1',
]