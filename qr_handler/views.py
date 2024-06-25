from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import QRScanHistory
import json


@login_required
def handle_qr_data(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data')
        try:
            data = json.loads(qr_data)
            # Здесь добавьте логику обработки QR-кода
            if 'user_id' in data:
                # Обработка запроса на добавление в друзья
                return handle_friend_request(request, data['user_id'])
            elif 'lecture_start' in data:
                # Обработка начала лекции
                return handle_lecture_start(request, data['lecture_start'])
            elif 'lecture_end' in data:
                # Обработка окончания лекции
                return handle_lecture_end(request, data['lecture_end'])
            elif 'purchase_id' in data:
                # Обработка покупки
                return handle_purchase(request, data['purchase_id'])
            else:
                return JsonResponse({'status': 'error', 'message': 'Unknown QR data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid QR data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def handle_friend_request(request, user_id):
    # Логика обработки запроса на добавление в друзья
    return JsonResponse({'status': 'ok', 'message': 'Friend request handled'})


def handle_lecture_start(request, lecture_id):
    # Логика обработки начала лекции
    return JsonResponse({'status': 'ok', 'message': 'Lecture start handled'})


def handle_lecture_end(request, lecture_id):
    # Логика обработки окончания лекции
    return JsonResponse({'status': 'ok', 'message': 'Lecture end handled'})


def handle_purchase(request, purchase_id):
    # Логика обработки покупки
    return JsonResponse({'status': 'ok', 'message': 'Purchase handled'})


from django.shortcuts import render


@login_required
def test_page(request):
    return render(request, 'qr_handler/test_page.html')
