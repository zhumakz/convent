from django.urls import path
from .views import registration_view, verify_login_view, profile_view, login_view

urlpatterns = [
    path('register/', registration_view, name='register'),
    path('verify_login/', verify_login_view, name='verify_login'),
    path('profile/', profile_view, name='profile'),
    path('login/', login_view, name='login'),
]
