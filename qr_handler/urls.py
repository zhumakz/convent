from django.urls import path
from .views import qr_scan_view, handle_qr_data, qr_friend_request, qr_purchase_detail, qr_campaign_vote, \
    qr_lecture_start, qr_lecture_end, friend_confirmation, qr_response_view, check_friend_request_status, \
    campaign_vote_confirmation, test_page

urlpatterns = [
    path('qr-scan/', qr_scan_view, name='qr_scan'),
    path('test_page/', test_page, name='qr_scan_test_page'),
    path('handle-qr-data/', handle_qr_data, name='handle_qr_data'),
    path('qr_friend_request/', qr_friend_request, name='qr_friend_request'),
    path('friend_confirmation/', friend_confirmation, name='friend_confirmation'),
    path('qr_purchase_detail/', qr_purchase_detail, name='qr_purchase_detail'),
    path('qr_campaign_vote/', qr_campaign_vote, name='qr_campaign_vote'),
    path('campaign_vote_confirmation/', campaign_vote_confirmation, name='campaign_vote_confirmation'),
    path('qr_lecture_start/', qr_lecture_start, name='qr_lecture_start'),
    path('qr_lecture_end/', qr_lecture_end, name='qr_lecture_end'),
    path('qr_response/', qr_response_view, name='qr_response'),
    path('check-friend-request-status/', check_friend_request_status, name='check_friend_request_status'),
]
