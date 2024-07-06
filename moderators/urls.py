from django.urls import path
from .views import moderator_dashboard, operator_view, handle_qr_data, transfer_coins, confirmation_view, seller_view,show_purchase_qr,m_response_view

urlpatterns = [
    path('dashboard/', moderator_dashboard, name='moderator_dashboard'),
    path('operator/', operator_view, name='operator'),
    path('handle_qr/', handle_qr_data, name='handle_qr_moderators'),
    path('transfer_coins/', transfer_coins, name='transfer_coins'),
    path('confirmation/', confirmation_view, name='confirmation'),
    path('seller/', seller_view, name='seller_view'),
    path('m_response/', m_response_view, name='m_response'),
    path('qr_code/<int:purchase_id>/', show_purchase_qr, name='show_purchase_qr'),
]
