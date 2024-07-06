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
from shop.services import ShopService

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
    transactions = CoinService.get_transactions(request.user).select_related('sender', 'recipient').order_by(
        '-timestamp')

    # Подсчитываем общее количество выданных монет
    total_coins_issued = sum(tx.amount for tx in transactions if tx.sender == request.user)

    return render(request, 'moderators/operator.html', {
        'transactions': transactions,
        'operator_name': f"{request.user.name} {request.user.surname}",
        'total_coins_issued': total_coins_issued
    })


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
@permission_required('moderators.add_coins', raise_exception=True)
def transfer_coins(request):
    user_id = request.session.get('qr_user_id')

    if not user_id:
        request.session['positiveResponse'] = False
        request.session['error_message'] = '2ID пользователя не найден в сессии.'
        request.session['redirect_url'] = 'operator'  # URL для перенаправления
        return redirect('m_response')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        request.session['positiveResponse'] = False
        request.session['error_message'] = 'Пользователь с данным ID не существует.'
        request.session['redirect_url'] = 'operator'  # URL для перенаправления
        return redirect('m_response')

    if request.method == 'POST':
        form = SendCoinsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            try:
                CoinService.create_transaction(
                    sender=request.user,
                    recipient=user,
                    amount=amount,
                    category_name='moderator_transfer'  # Используем категорию транзакции moderator_transfer
                )
                # Сохранение данных о транзакции в сессии
                request.session['confirmation_user'] = user_id
                request.session['confirmation_amount'] = str(amount)  # Преобразование в строку

                # Очистка user_id из сессии после успешного перевода
                del request.session['qr_user_id']
                return redirect('confirmation')
            except Exception as e:
                request.session['positiveResponse'] = False
                request.session['error_message'] = f'Ошибка при проведении транзакции: {e}'
                request.session['redirect_url'] = 'operator'  # URL для перенаправления
                return redirect('m_response')
        else:
            request.session['positiveResponse'] = False
            request.session['error_message'] = 'Некорректные данные формы.'
            request.session['redirect_url'] = 'operator'  # URL для перенаправления
            return redirect('m_response')
    else:
        form = SendCoinsForm(initial={'user_id': user.id})

    return render(request, 'moderators/transfer_coins.html', {
        'form': form,
        'recipient': user,
        'user_balance': user.doscointbalance.balance
    })

@login_required
def confirmation_view(request):
    user_id = request.session.get('confirmation_user')

    if not user_id:
        request.session['positiveResponse'] = False
        request.session['error_message'] = '3ID пользователя не найден в сессии.'
        request.session['redirect_url'] = 'operator'  # URL для перенаправления
        return redirect('m_response')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        request.session['positiveResponse'] = False
        request.session['error_message'] = 'Пользователь с данным ID не существует.'
        request.session['redirect_url'] = 'operator'  # URL для перенаправления
        return redirect('m_response')

    amount = request.session.get('confirmation_amount')
    if not user or not amount:
        request.session['positiveResponse'] = False
        request.session['error_message'] = 'Информация о транзакции не найдена в сессии.'
        request.session['redirect_url'] = 'operator'  # URL для перенаправления
        return redirect('m_response')

    # Очистка данных о транзакции из сессии
    del request.session['confirmation_user']
    del request.session['confirmation_amount']

    return render(request, 'moderators/confirmation.html', {
        'recipient': user,
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
            request.session['positiveResponse'] = False
            request.session['error_message'] = 'Некорректные данные формы.'
            request.session['redirect_url'] = 'seller_view'
            return redirect('m_response')
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


@login_required
@permission_required('moderators.add_coins', raise_exception=True)
def check_purchase_status(request, purchase_id):
    purchase = ShopService.get_purchase_by_id(purchase_id)

    if purchase.is_completed:
        request.session['positiveResponse'] = True
        request.session['error_message'] = 'Покупка успешно завершена!'
        request.session['redirect_url'] = 'seller_view'
        return JsonResponse({'status': 'completed'})
    elif purchase.is_cancelled:
        request.session['positiveResponse'] = False
        request.session['error_message'] = 'Покупка была отменена.'
        request.session['redirect_url'] = 'seller_view'
        return JsonResponse({'status': 'cancelled'})
    else:
        return JsonResponse({'status': 'pending'})
@login_required
def m_response_view(request):
    positive_response = request.session.get('positiveResponse', False)
    error_message = request.session.get('error_message', 'Unknown error')
    redirect_url = request.session.get('redirect_url', 'moderator_dashboard')
    context = {
        'positiveResponse': positive_response,
        'error_message': error_message,
        'redirect_url': redirect_url,
    }
    return render(request, 'moderators/m_response.html', context)