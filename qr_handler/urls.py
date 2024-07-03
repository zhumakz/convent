from django.urls import path
from .views import qr_scan_view, handle_qr_data, qr_friend_request, qr_purchase_detail, qr_campaign_vote, qr_lecture_start, qr_lecture_end,friend_confirmation

urlpatterns = [
    path('qr-scan/', qr_scan_view, name='qr_scan'),
    path('handle-qr-data/', handle_qr_data, name='handle_qr_data'),
    path('qr_friend_request/', qr_friend_request, name='qr_friend_request'),
    path('friend_confirmation/', friend_confirmation, name='friend_confirmation'),
    path('qr_purchase_detail/', qr_purchase_detail, name='qr_purchase_detail'),
    path('qr_campaign_vote/', qr_campaign_vote, name='qr_campaign_vote'),
    path('qr_lecture_start/', qr_lecture_start, name='qr_lecture_start'),
    path('qr_lecture_end/', qr_lecture_end, name='qr_lecture_end'),
]
