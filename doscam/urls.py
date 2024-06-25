from django.urls import path
from . import views

urlpatterns = [
    path('operator/', views.operator_view, name='operator_view'),
    path('scan_qr/<str:qr_data>/', views.scan_qr_code_view, name='scan_qr_code_view'),
    path('create_event/', views.create_event_view, name='create_event_view'),
    path('event/<int:event_id>/', views.event_detail_view, name='event_detail_view'),
]
