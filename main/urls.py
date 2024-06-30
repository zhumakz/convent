from django.urls import path
from .views import home_view, switch_language, select_language

urlpatterns = [
    path('', home_view, name='home'),
    path('select-language/', select_language, name='select_language'),
    path('switch-language/<str:lang_code>/', switch_language, name='switch_language'),
]
