from django.urls import path
from accounts.views import login_and_verify_view

urlpatterns = [
    path('verify_sms/', login_and_verify_view, name='verify_sms'),
    path('resend_sms/', login_and_verify_view, name='resend_sms'),
]
