from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from campaigns.services import CampaignService
from convent import settings
from friends.models import FriendRequest
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
                    return redirect('profile')

            except json.JSONDecodeError:
                # Обработка ошибки декодирования JSON
                return JsonResponse({'error': 'Invalid QR data'}, status=400)

    return redirect('profile')


@login_required
def qr_friend_request(request):
    data = request.session.get('qr_data')
    if not data:
        return redirect('profile')

    user_id = data.get('user_id')

    try:
        to_user = User.objects.get(id=user_id)

        # Проверка, если уже дружат
        if FriendService.are_friends(request.user, to_user):
            request.session['qr_data']['user_id'] = to_user.id  # Обновляем данные в сессии
            return redirect('friend_confirmation')

        success, message = FriendService.send_friend_request(request.user, to_user)
        if success:
            request.session['qr_data']['user_id'] = to_user.id  # Обновляем данные в сессии
            return redirect('friend_confirmation')
        context = {
            'message': message,
            'success': success,
            'to_user': to_user,
            'qr_code_url': request.user.qr_code
        }
        return render(request, 'qr_handler/qr_friend_request.html', context)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except ValidationError as e:
        context = {
            'message': e.messages[0],
            'success': False,
            'to_user': None,
            'qr_code_url': None,
        }
        return render(request, 'qr_handler/qr_friend_request.html', context)


@login_required
def friend_confirmation(request):
    data = request.session.get('qr_data')
    if not data:
        return redirect('profile')

    user_id = data.get('user_id')

    try:
        to_user = User.objects.get(id=user_id)
        coins_transferred = 5  #  settings.FRIEND_REWARD_COINS  Предполагаем, что это количество коинов за дружбу
        context = {
            'to_user': to_user,
            'coins_transferred': coins_transferred
        }
        return render(request, 'qr_handler/friend_confirmation.html', context)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@login_required
def qr_purchase_detail(request):
    data = request.session.get('qr_data')
    if not data:
        return redirect('profile')

    purchase_id = data.get('purchase_id')
    purchase = ShopService.get_purchase_by_id(purchase_id)

    user_balance = request.user.doscointbalance.balance  # Предполагаем, что у пользователя есть атрибут баланса

    if request.method == 'POST':
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
        return render(request, 'qr_handler/purchase_confirmation.html', context)

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

    if request.method == 'POST':
        try:
            message = CampaignService.vote_for_campaign(request.user, campaign)
            success = True
        except ValidationError as e:
            message = e.messages[0]
            success = False
    else:
        success = None
        message = None

    voted = CampaignService.user_has_voted(request.user, campaign)

    context = {
        'message': message,
        'success': success,
        'campaign': campaign,
        'voted': voted,
    }
    return render(request, 'qr_handler/qr_campaign_vote.html', context)


@login_required
def qr_lecture_start(request):
    data = request.session.get('qr_data')
    if not data:
        return redirect('profile')

    lecture_id = data.get('lecture_start')  # Предполагаем, что в данных QR-кода есть идентификатор лекции
    lecture = LectureService.get_lecture_by_id(lecture_id)

    success, message = LectureService.register_lecture_start(request.user, lecture)
    lecture_passed = LectureService.get_attendance(request.user, lecture).end_scanned
    coins_transferred = settings.LECTURE_REWARD_COINS if lecture_passed else 0

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
        return redirect('profile')

    lecture_id = data.get('lecture_end')  # Предполагаем, что в данных QR-кода есть идентификатор лекции
    lecture = LectureService.get_lecture_by_id(lecture_id)

    success, message = LectureService.register_lecture_end(request.user, lecture)
    lecture_passed = LectureService.get_attendance(request.user, lecture).end_scanned
    coins_transferred = settings.LECTURE_REWARD_COINS if lecture_passed else 0

    context = {
        'message': message,
        'success': success,
        'lecture': lecture,
        'lecturePassed': lecture_passed,
        'coins_transferred': coins_transferred
    }
    return render(request, 'qr_handler/qr_lecture_detail.html', context)
