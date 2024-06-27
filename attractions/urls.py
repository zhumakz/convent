from django.urls import path
from .views import attraction_list, attraction_detail, create_attraction, edit_attraction

urlpatterns = [
    path('', attraction_list, name='attraction_list'),
    path('<int:attraction_id>/', attraction_detail, name='attraction_detail'),
    path('create/', create_attraction, name='create_attraction'),
    path('<int:attraction_id>/edit/', edit_attraction, name='edit_attraction'),
]
