from django.urls import path
from .views import moderator_dashboard, operator_view

urlpatterns = [
    path('dashboard/', moderator_dashboard, name='moderator_dashboard'),
    path('operator/', operator_view, name='operator'),
]
