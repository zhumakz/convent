from django.urls import path
from .views import user_qr_code_view

urlpatterns = [
    path('user/<int:user_id>/', user_qr_code_view, name='user_qr_code'),
]
