from django.urls import path
from .views import process_qr_code, user_qr_code_view

urlpatterns = [
    path('process_qr_code/<str:encrypted_id>/', process_qr_code, name='process_qr_code'),
    path('user_qr_code/<int:user_id>/', user_qr_code_view, name='user_qr_code'),
]
