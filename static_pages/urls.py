from django.urls import path

from .models import StaticPage
from .views import static_page_list, static_page_detail

urlpatterns = [
    path('', static_page_list, name='static_page_list'),
    path('<int:page_id>/', static_page_detail, name='static_page_detail'),
    path('about-coins/', static_page_detail, {'page_id': StaticPage.objects.get(title='about-coins').id},
         name='about_coins'),
    path('map/', static_page_detail, {'page_id': StaticPage.objects.get(title='map').id}, name='map'),
]
