from django.urls import path
from .views import send_friend_request, confirm_friend_request, friend_requests, friends_list

urlpatterns = [
    path('send_friend_request/', send_friend_request, name='send_friend_request'),
    path('confirm_friend_request/<int:request_id>/', confirm_friend_request, name='confirm_friend_request'),
    path('friend_requests/', friend_requests, name='friend_requests'),
    path('friends_list/', friends_list, name='friends_list'),
]
