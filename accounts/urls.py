from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import registration_view, verify_login_view, profile_view, login_view, logout_view, profile_edit_view

urlpatterns = [
    path('register/', registration_view, name='register'),
    path('verify_login/', verify_login_view, name='verify_login'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
