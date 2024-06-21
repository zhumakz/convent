from django.urls import path
from .views import lecture_list, lecture_detail, scan_lecture_qr_start, scan_lecture_qr_end

urlpatterns = [
    path('', lecture_list, name='lecture_list'),
    path('<int:lecture_id>/', lecture_detail, name='lecture_detail'),
    path('<int:lecture_id>/scan_start/', scan_lecture_qr_start, name='scan_lecture_qr_start'),
    path('<int:lecture_id>/scan_end/', scan_lecture_qr_end, name='scan_lecture_qr_end'),
]
