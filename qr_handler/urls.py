from django.urls import path
from django.views.generic import TemplateView
from .views import qr_scan_view, handle_qr_data, operation_error

urlpatterns = [
    path('qr-scan/', qr_scan_view, name='qr_scan'),
    path('handle-qr-data/', handle_qr_data, name='handle_qr_data'),
    path('friend-request-success/', TemplateView.as_view(template_name='qr_handler/friend_request_success.html'), name='friend_request_success'),
    path('lecture-start-success/', TemplateView.as_view(template_name='lecture_start_success.html'), name='lecture_start_success'),
    path('lecture-end-success/', TemplateView.as_view(template_name='lecture_end_success.html'), name='lecture_end_success'),
    path('purchase-success/', TemplateView.as_view(template_name='purchase_success.html'), name='purchase_success'),
    path('event-success/', TemplateView.as_view(template_name='event_success.html'), name='event_success'),
    path('operation-error/', operation_error, name='operation_error'),
]
