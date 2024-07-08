# badges/urls.py
from django.urls import path
from .views import generate_badge

urlpatterns = [
    path('generate/<int:user_id>/', generate_badge, name='generate_badge'),
]
