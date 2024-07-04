from django.urls import path
from .views import registration_view, login_and_verify_view, profile_view, profile_edit_view, user_profile_view, \
    logout_view, moderator_login_view, selfie_view,registration_success_view

urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', login_and_verify_view, name='login'),
    path('verify_login/', login_and_verify_view, name='verify_login'),
    path('resend_sms/', login_and_verify_view, name='resend_sms'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('profile/<int:user_id>/', user_profile_view, name='user_profile'),
    path('logout/', logout_view, name='logout'),
    path('moderator/login/', moderator_login_view, name='moderator_login'),
    path('selfie/', selfie_view, name='selfie'),
    path('registration-success/', registration_success_view, name='registration_success'),
]
