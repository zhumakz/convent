"""
WSGI config for convent project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'convent.settings')

application = get_wsgi_application()

# Регистрация сигналов после полной загрузки приложения
from coins.signals_register import register_signals

register_signals()
