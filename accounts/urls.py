from django.urls import path
from .views import registration_view, login_view, verify_login_view, profile_view, profile_edit_view, user_profile_view, logout_view, resend_sms_view

urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', login_view, name='login'),
    path('verify_login/', verify_login_view, name='verify_login'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('profile/<int:user_id>/', user_profile_view, name='user_profile'),
    path('logout/', logout_view, name='logout'),
    path('resend_sms/', resend_sms_view, name='resend_sms'),
]
