import json
import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from accounts.models import User
from coins.services import CoinService
from moderators.forms import SendCoinsForm
from shop.forms import PurchaseForm
from shop.models import Purchase

logger = logging.getLogger('moderators')


def is_moderator(user):
    return user.groups.filter(name__in=['Главный оператор', 'Оператор', 'Продавец', 'Оператор Doscam']).exists()


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

            user_id = data['user_id']
            user = get_object_or_404(User, id=user_id)

            if user.is_admin or user.is_moderator:
                logger.warning("User is an admin or moderator")
                return JsonResponse({'status': 'error', 'message': 'User is an admin or moderator'})

            # Сохранение user_id в сессии
            request.session['qr_user_id'] = user.id

            return JsonResponse({'status': 'ok', 'redirect_url': reverse('transfer_coins')})

        except json.JSONDecodeError:
            logger.error("Invalid QR data: %s", qr_data)
            return JsonResponse({'status': 'error', 'message': 'Invalid QR data'})
        except Exception as e:
            logger.error("Error handling QR data: %s", e, exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
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
    user_id = request.session.get('qr_user_id')

    if not user_id:
        messages.error(request, 'User ID not found in session.')
        return redirect('operator')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User with given ID does not exist.')
        return redirect('operator')

    if request.method == 'POST':
        form = SendCoinsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            try:
                CoinService.create_transaction(
                    sender=request.user,
                    recipient=user,
                    amount=amount,
                    description=description
                )
                # Сохранение данных о транзакции в сессии
                request.session['confirmation_user_name'] = f"{user.name} {user.surname}"
                request.session['confirmation_amount'] = str(amount)  # Преобразование в строку

                # Очистка user_id из сессии после успешного перевода
                del request.session['qr_user_id']
                return redirect('confirmation')
            except Exception as e:
                messages.error(request, f'Error during transaction: {e}')
        else:
            messages.error(request, 'Invalid form data.')
    else:
        form = SendCoinsForm(initial={'user_id': user.id})

    return render(request, 'moderators/transfer_coins.html', {
        'form': form,
        'user_name': f"{user.name} {user.surname}",
        'user_balance': user.doscointbalance.balance
    })



@login_required
def confirmation_view(request):
    user_name = request.session.get('confirmation_user_name')
    amount = request.session.get('confirmation_amount')

    if not user_name or not amount:
        messages.error(request, 'Transaction information not found in session.')
        return redirect('operator')

    # Очистка данных о транзакции из сессии
    del request.session['confirmation_user_name']
    del request.session['confirmation_amount']

    return render(request, 'moderators/confirmation.html', {
        'user_name': user_name,
        'amount': amount
    })

@login_required
@permission_required('moderators.add_coins', raise_exception=True)
def seller_view(request):
    # Получаем историю завершенных продаж
    transactions = Purchase.objects.filter(seller=request.user, is_completed=True).order_by('-created_at')

    # Подсчитываем общий баланс продавца
    total_sales = sum(tx.amount for tx in transactions)

    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.seller = request.user
            purchase.save()

            messages.success(request, 'QR код успешно сгенерирован!')
            return redirect('show_purchase_qr', purchase_id=purchase.id)
    else:
        form = PurchaseForm()

    return render(request, 'moderators/seller.html', {
        'transactions': transactions,
        'seller_name': f"{request.user.name} {request.user.surname}",
        'total_sales': total_sales,
        'form': form,
    })

@login_required
@permission_required('moderators.add_coins', raise_exception=True)
def show_purchase_qr(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    return render(request, 'moderators/qr_code.html', {
        'purchase': purchase,
        'qr_code_url': purchase.qr_code.url,
    })