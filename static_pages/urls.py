from django.urls import path
from .views import static_page_list, static_page_detail

urlpatterns = [
    path('', static_page_list, name='static_page_list'),
    path('<int:page_id>/', static_page_detail, name='static_page_detail'),
]
