from django.urls import path
from .views import lecture_list, lecture_detail, show_qr_start, show_qr_end

urlpatterns = [
    path('', lecture_list, name='lecture_list'),
    path('<int:lecture_id>/', lecture_detail, name='lecture_detail'),
    path('<int:lecture_id>/show_qr_start/', show_qr_start, name='show_qr_start'),
    path('<int:lecture_id>/show_qr_end/', show_qr_end, name='show_qr_end'),
]
