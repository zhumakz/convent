from django.urls import path
from .views import top_users_view, top_campaigns_view

urlpatterns = [
    path('top-users/', top_users_view, name='top_users'),
    path('top-campaigns/', top_campaigns_view, name='top_campaigns'),
]
