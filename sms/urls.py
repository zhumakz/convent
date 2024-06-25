from django.urls import path
from accounts.views import verify_login_view, resend_sms_view

urlpatterns = [
    path('verify_sms/', verify_login_view, name='verify_sms'),
    path('resend_sms/', resend_sms_view, name='resend_sms'),
]
