from django.urls import path
from . import views

urlpatterns = [
    path('', views.attraction_list, name='attraction_list'),
    path('attractions/<int:attraction_id>/', views.attraction_detail, name='attraction_detail'),
    path('attractions/<int:attraction_id>/json/', views.attraction_detail_json, name='attraction_detail_json'),
    path('attractions/create/', views.create_attraction, name='create_attraction'),
    path('attractions/<int:attraction_id>/edit/', views.edit_attraction, name='edit_attraction'),
]
