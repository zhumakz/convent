from django.urls import path
from .views import static_page_list, static_page_detail, about_coins_view, map_view,policy_view,user_agreement_view

urlpatterns = [
    path('', static_page_list, name='static_page_list'),
    path('<int:page_id>/', static_page_detail, name='static_page_detail'),
    path('about-coins/', about_coins_view, name='about_coins'),
    path('map/', map_view, name='map'),
    path('policy/', policy_view, name='policy'),
    path('user-agreement/', user_agreement_view, name='user_agreement'),
]
