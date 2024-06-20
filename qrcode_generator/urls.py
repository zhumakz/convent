from django.urls import path
from .views import user_qr_code_view, process_qr_code

urlpatterns = [
    path('user/<int:user_id>/', user_qr_code_view, name='user_qr_code'),
    path('process/<str:encrypted_id>/', process_qr_code, name='process_qr_code'),
]
