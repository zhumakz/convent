from django.urls import path
from .views import top_users_view

urlpatterns = [
    path('top-users/', top_users_view, name='top_users'),
]
