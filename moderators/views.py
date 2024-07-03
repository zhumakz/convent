import json
import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from accounts.models import User
from coins.services import CoinService
from moderators.forms import SendCoinsForm

logger = logging.getLogger('moderators')


def is_moderator(user):
    return user.groups.filter(name__in=['Главный оператор', 'Оператор', 'Продавец', 'Оператор Doscam']).exists()


@login_required
@permission_required('moderators.view_moderators', raise_exception=True)
def moderator_dashboard(request):
    return render(request, 'moderators/dashboard.html')


@login_required
@permission_required('moderators.add_coins', raise_exception=True)
def operator_view(request):
    # Получаем историю переводов
    transactions = CoinService.get_transactions(request.user).select_related('sender', 'recipient').order_by('-timestamp')

    # Обрабатываем историю переводов для отображения
    processed_transactions = [CoinService.process_transaction(tx, request.user) for tx in transactions]

    # Подсчитываем общее количество выданных монет
    total_coins_issued = sum(tx.amount for tx in transactions if tx.sender == request.user)

    return render(request, 'moderators/operator.html', {
        'transactions': processed_transactions,
        'operator_name': f"{request.user.name} {request.user.surname}",
        'total_coins_issued': total_coins_issued
    })

@login_required
@permission_required('moderators.add_coins', raise_exception=True)
def transfer_coins(request):
    if request.method == 'POST':
        form = SendCoinsForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            try:
                recipient = User.objects.get(id=user_id)
                CoinService.create_transaction(
                    sender=request.user,
                    recipient=recipient,
                    amount=amount,
                    description=description
                )
                return JsonResponse({'status': 'ok', 'message': 'Coins successfully sent.'})
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User with given ID does not exist.'})
        return JsonResponse({'status': 'error', 'message': 'Invalid form data.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def handle_qr_data(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data')

        if not qr_data:
            logger.error("No QR data received")
            return JsonResponse({'status': 'error', 'message': 'No QR data received'}, status=400)

        try:
            logger.info(f"Received QR data: {qr_data}")
            data = json.loads(qr_data)

            if 'user_id' not in data:
                return JsonResponse({'status': 'error', 'message': 'Invalid QR data'})

            return handle_user_info(request, data['user_id'])

        except json.JSONDecodeError:
            logger.error("Invalid QR data: %s", qr_data)
            return JsonResponse({'status': 'error', 'message': 'Invalid QR data'})
        except Exception as e:
            logger.error("Error handling QR data: %s", e, exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def handle_user_info(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)

        if user.is_admin or user.is_moderator:
            logger.warning("User is an admin or moderator")
            return JsonResponse({'status': 'error', 'message': 'User is an admin or moderator'})

        return JsonResponse({
            'status': 'ok',
            'user_info': {
                'name': f"{user.name} {user.surname}",
                'user_id': user.id,
                'balance': user.doscointbalance.balance
            }
        })
    except Exception as e:
        logger.error("Error handling user info: %s", e, exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
