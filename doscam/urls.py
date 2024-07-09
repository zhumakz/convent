from django.urls import path

from .views import create_event, event_detail, operator_view, confirm_participation, randomize_participants, \
    publish_event, stop_event, find_view, dos_desktop_view, handle_qr_data, qr_scan_view

urlpatterns = [
    path('create/', create_event, name='create_event'),
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('operator/', operator_view, name='operator_view'),
    path('confirm/<int:user_id>/', confirm_participation, name='confirm_participation'),
    path('randomize/', randomize_participants, name='randomize_participants'),
    path('publish/<int:event_id>/', publish_event, name='publish_event'),
    path('stop/<int:event_id>/', stop_event, name='stop_event'),
    path('find/', find_view, name='doscam_find'),
    path('panel/', dos_desktop_view, name='dos_desktop_view'),
    path('handle-qr-data/', handle_qr_data, name='handle_qr_doscam'),
    path('qr/', qr_scan_view, name='qr_doscam'),
]
