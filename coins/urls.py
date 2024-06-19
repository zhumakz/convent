from django.urls import path
from . import views

urlpatterns = [
    path('balance/', views.balance_view, name='balance'),
    path('add-coins/', views.add_coins_view, name='add_coins'),
    path('remove-coins/', views.remove_coins_view, name='remove_coins'),
]
