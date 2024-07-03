from django.urls import path
from .views import moderator_dashboard, operator_view, handle_qr_data, transfer_coins

urlpatterns = [
    path('dashboard/', moderator_dashboard, name='moderator_dashboard'),
    path('operator/', operator_view, name='operator'),
    path('handle_qr/', handle_qr_data, name='handle_qr_moderators'),
    path('transfer_coins/', transfer_coins, name='transfer_coins'),
]
