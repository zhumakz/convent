from django.urls import path
from .views import shop_list, product_list, generate_purchase_qr, scan_qr

urlpatterns = [
    path('', shop_list, name='shop_list'),
    path('<int:shop_id>/products/', product_list, name='product_list'),
    path('generate_qr/', generate_purchase_qr, name='generate_purchase_qr'),
    path('scan_qr/', scan_qr, name='scan_qr'),
]
