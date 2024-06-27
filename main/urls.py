from django.urls import path
from .views import home_view,switch_language

urlpatterns = [
    path('', home_view, name='home'),
    path('switch_language/<str:lang_code>/', switch_language, name='switch_language'),
]
