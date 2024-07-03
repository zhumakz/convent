from django.urls import path
from .views import qr_scan_view, handle_qr_data, qr_friend_request, qr_purchase_detail, qr_campaign_vote, \
    qr_lecture_detail

urlpatterns = [
    path('qr-scan/', qr_scan_view, name='qr_scan'),
    path('handle-qr-data/', handle_qr_data, name='handle_qr_data'),
    path('qr_friend_request/', qr_friend_request, name='qr_friend_request'),
    path('qr_purchase_detail/<int:purchase_id>/', qr_purchase_detail, name='qr_purchase_detail'),
    path('qr_campaign_vote/<str:campaign_vote>/', qr_campaign_vote, name='qr_campaign_vote'),
    path('qr_lecture_detail/<str:lecture_start>/<str:lecture_end>/', qr_lecture_detail, name='qr_lecture_detail'),
]
