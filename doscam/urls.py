from django.urls import path
from .views import create_event, event_detail, operator_view, confirm_participation

urlpatterns = [
    path('create/', create_event, name='create_event'),
    path('event/', event_detail, name='event_detail'),
    path('operator/', operator_view, name='operator_view'),
    path('confirm/<int:user_id>/', confirm_participation, name='confirm_participation'),
]
