from django.urls import path
from . import views

urlpatterns = [
    path('', views.point_list, name='point_list'),
]
