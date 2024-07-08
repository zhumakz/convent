from decimal import Decimal

from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from campaigns.services import CampaignService
from coins.services import CoinService
from convent import settings
from friends.models import FriendRequest, Friendship
from lectures.models import Lecture
from coins.models import Transaction
from accounts.models import User
from friends.services import FriendService
import logging

from lectures.services import LectureService
from shop.models import Purchase
from shop.services import ShopService

logger = logging.getLogger(__name__)


@login_required
def test_page(request):
    return render(request, 'qr_handler/test_page.html')


@login_required
def qr_scan_view(request):
    # Отображение страницы с формой для сканирования QR-кода
    return render(request, 'qr_handler/qr.html')


@login_required
def handle_qr_data(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data')
        if qr_data:
            try:
                data = json.loads(qr_data)
                user_id = data.get('user_id')
                lecture_start = data.get('lecture_start')
                lecture_end = data.get('lecture_end')
                purchase_id = data.get('purchase_id')
                campaign_vote = data.get('campaign_vote')

                # Сохранение данных в сессии
                request.session['qr_data'] = data

                # Логика перенаправления в зависимости от данных QR-кода
                if user_id:
                    return redirect('qr_friend_request')
                elif purchase_id:
                    return redirect('qr_purchase_detail')
                elif campaign_vote:
                    return redirect('qr_campaign_vote')
                elif lecture_start:
                    return redirect('qr_lecture_start')
                elif lecture_end:
                    return redirect('qr_lecture_end')
                else:
                    request.session['error_message'] = 'Недействительные данные QR'
                    request.session['positiveResponse'] = False
                    return redirect('qr_response')

            except json.JSONDecodeError:
                request.session['error_message'] = 'Недействительные данные QR'
                request.session['positiveResponse'] = False
                return redirect('qr_response')

    request.session['error_message'] = 'Неверный запрос'
    request.session['positiveResponse'] = False
    return redirect('qr_response')


@login_required
def qr_friend_request(request):
    data = request.session.get('qr_data')
    if not data:
        request.session['error_message'] = 'Данные QR не найдены'
        request.session['positiveResponse'] = False
        return redirect('qr_response')

    user_id = data.get('user_id')

    try:
        to_user = User.objects.get(id=user_id)

        # Проверка, если уже дружат
        if FriendService.are_friends(request.user, to_user):
            request.session['qr_data']['user_id'] = to_user.id  # Обновляем данные в сессии
            request.session['positiveResponse'] = True
            request.session['error_message'] = 'Вы уже друзья!'
            return redirect('qr_response')

        # Попытка отправить запрос дружбы
        state, message, coins_transferred = FriendService.send_friend_requestQR(request.user, to_user)

        if state == 'new_request' or state == 'already_sent':
            # В любом случае показываем qr_friend_request
            context = {
                'message': message,
                'success': state == 'new_request',
                'to_user': to_user,
                'qr_code_url': request.user.qr_code
            }
            return render(request, 'qr_handler/qr_friend_request.html', context)

        elif state == 'now_friends':
            request.session['qr_data']['user_id'] = to_user.id  # Обновляем данные в сессии
            request.session['coins_transferred'] = str(coins_transferred)  # Сохраняем количество коинов
            return redirect('friend_confirmation')

        elif state == 'error':
            request.session['error_message'] = message
            request.session['positiveResponse'] = False
            return redirect('qr_response')

    except User.DoesNotExist:
        request.session['error_message'] = 'Пользователь не найден'
        request.session['positiveResponse'] = False
        return redirect('qr_response')
    except ValidationError as e:
        request.session['error_message'] = e.messages[0]
        request.session['positiveResponse'] = False
        return redirect('qr_response')


@login_required
def friend_confirmation(request):
    data = request.session.get('qr_data')
    if not data:
        request.session['error_message'] = 'Данные QR не найдены'
        request.session['positiveResponse'] = False
        return redirect('qr_response')

    user_id = data.get('user_id')
    coins_transferred_str = request.session.get('coins_transferred')

    if not coins_transferred_str:
        return redirect('profile')

    try:
        to_user = User.objects.get(id=user_id)
        coins_transferred = Decimal(coins_transferred_str)  # Преобразование строки обратно в Decimal
        context = {
            'to_user': to_user,
            'coins_transferred': coins_transferred
        }
        return render(request, 'qr_handler/friend_confirmation.html', context)
    except User.DoesNotExist:
        request.session['error_message'] = 'Пользователь не найден'
        request.session['positiveResponse'] = False
        return redirect('qr_response')


@login_required
def check_friend_request_status(request):
    data = request.session.get('qr_data')
    if not data:
        return JsonResponse({'status': 'error', 'message': 'Данные QR не найдены'}, status=400)

    user_id = data.get('user_id')
    try:
        to_user = User.objects.get(id=user_id)
        # Проверка, если уже дружат
        if FriendService.are_friends(request.user, to_user):
            return JsonResponse({'status': 'confirmed'})
        return JsonResponse({'status': 'pending'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Пользователь не найден'}, status=404)


@login_required
def qr_purchase_detail(request):
    data = request.session.get('qr_data')
    if not data:
        request.session['error_message'] = 'Данные QR не найдены'
        request.session['positiveResponse'] = False
        return redirect('qr_response')

    purchase_id = data.get('purchase_id')
    purchase = ShopService.get_purchase_by_id(purchase_id)

    if not purchase:
        request.session['error_message'] = 'Покупка не найдена'
        request.session['positiveResponse'] = False
        return redirect('qr_response')

    if purchase.is_completed:
        request.session['error_message'] = 'Этот QR-код уже использован для завершения покупки.'
        request.session['positiveResponse'] = False
        return redirect('qr_response')

    user_balance = request.user.doscointbalance.balance  # Предполагаем, что у пользователя есть атрибут баланса

    if request.method == 'POST':
        if 'confirm' in request.POST:
            try:
                message = ShopService.complete_purchase(purchase, request.user)
                success = True
            except ValidationError as e:
                message = e.messages[0]
                success = False

            coins_transferred = purchase.amount if success else 0
            context = {
                'message': message,
                'success': success,
                'purchase': purchase,
                'coins_transferred': coins_transferred
            }
            request.session['positiveResponse'] = success
            request.session['error_message'] = message
            return redirect('qr_response')

        elif 'cancel' in request.POST:
            purchase.is_cancelled = True
            purchase.save()
            request.session['positiveResponse'] = False
            request.session['error_message'] = 'Покупка была отменена.'
            return redirect('profile')

    context = {
        'purchase': purchase,
        'user_balance': user_balance,
        'purchase_amount': purchase.amount
    }
    return render(request, 'qr_handler/qr_purchase_detail.html', context)


@login_required
def qr_campaign_vote(request):
    data = request.session.get('qr_data')
    if not data:
        return redirect('profile')

    campaign_id = data.get('campaign_vote')
    campaign = CampaignService.get_campaign_by_id(campaign_id)

    messages = request.session.pop('error_messages', [])

    # Проверка, голосовал ли пользователь за какую-либо кампанию
    previous_vote = CampaignService.get_previous_vote(request.user)
    if previous_vote:
        message = f"Вы уже отдали свой голос за '{previous_vote.campaign.name}'."
        messages.append(message)
        context = {
            'messages': messages,
            'campaign': campaign,
            'voted': True,
        }
        return render(request, 'qr_handler/qr_campaign_vote.html', context)

    if request.method == 'POST':
        try:
            transaction, message = CampaignService.vote_for_campaign(request.user, campaign)
            request.session['positiveResponse'] = True
            request.session['error_messages'] = [message]
            request.session['campaign_id'] = campaign.id
            request.session['coins_transferred'] = str(transaction.amount)  # Преобразование Decimal в строку
            return redirect('campaign_vote_confirmation')
        except ValidationError as e:
            messages = e.messages
            request.session['positiveResponse'] = False
            request.session['error_messages'] = messages
            return redirect('qr_response')

    voted = CampaignService.user_has_voted(request.user, campaign)

    context = {
        'messages': messages,
        'campaign': campaign,
        'voted': voted,
    }
    return render(request, 'qr_handler/qr_campaign_vote.html', context)


@login_required
def campaign_vote_confirmation(request):
    # Извлечение данных из сессии
    campaign_id = request.session.get('campaign_id')
    coins_transferred_str = request.session.get('coins_transferred')
    error_message = request.session.get('error_message')

    if not campaign_id or not coins_transferred_str:
        return redirect('profile')

    campaign = CampaignService.get_campaign_by_id(campaign_id)
    coins_transferred = Decimal(coins_transferred_str)  # Преобразование строки обратно в Decimal

    context = {
        'campaign': campaign,
        'coins_transferred': coins_transferred,
        'error_message': error_message,
    }

    return render(request, 'qr_handler/campaign_vote_confirmation.html', context)


@login_required
def qr_lecture_start(request):
    data = request.session.get('qr_data')
    if not data:
        request.session['error_message'] = 'Данные QR не найдены'
        request.session['positiveResponse'] = False
        return redirect('qr_response')

    lecture_id = data.get('lecture_start')  # Предполагаем, что в данных QR-кода есть идентификатор лекции
    lecture = LectureService.get_lecture_by_id(lecture_id)

    success, message = LectureService.register_lecture_start(request.user, lecture)
    attendance = LectureService.get_attendance(request.user, lecture)

    lecture_passed = attendance.end_scanned if attendance else False

    try:
        coins_transferred = CoinService.get_price_by_category_name('lecture_bonus') if lecture_passed else 0
    except ValidationError:
        coins_transferred = 0

    context = {
        'message': message,
        'success': success,
        'lecture': lecture,
        'lecturePassed': lecture_passed,
        'coins_transferred': coins_transferred
    }
    return render(request, 'qr_handler/qr_lecture_detail.html', context)


@login_required
def qr_lecture_end(request):
    data = request.session.get('qr_data')
    if not data:
        request.session['error_message'] = 'Данные QR не найдены'
        request.session['positiveResponse'] = False
        return redirect('qr_response')

    lecture_id = data.get('lecture_end')  # Предполагаем, что в данных QR-кода есть идентификатор лекции
    lecture = LectureService.get_lecture_by_id(lecture_id)

    success, message = LectureService.register_lecture_end(request.user, lecture)
    attendance = LectureService.get_attendance(request.user, lecture)

    lecture_passed = attendance.end_scanned if attendance else False

    try:
        coins_transferred = CoinService.get_price_by_category_name('lecture_bonus') if lecture_passed else 0
    except ValidationError:
        coins_transferred = 0

    context = {
        'message': message,
        'success': success,
        'lecture': lecture,
        'lecturePassed': lecture_passed,
        'coins_transferred': coins_transferred
    }
    return render(request, 'qr_handler/qr_lecture_detail.html', context)


@login_required
def qr_response_view(request):
    positive_response = request.session.get('positiveResponse', False)
    error_message = request.session.get('error_message', 'Неизвестная ошибка')
    context = {
        'positiveResponse': positive_response,
        'error_message': error_message,
    }
    return render(request, 'qr_handler/qr_response.html', context)
