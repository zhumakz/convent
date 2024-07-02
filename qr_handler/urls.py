from django.urls import path
from . import views

urlpatterns = [
    path('handle/', views.handle_qr_data, name='handle_qr_data'),
    path('test/', views.test_page, name='test_page'),
    path('qr-scan/', views.qr_scan_view, name='qr_scan'),
]
