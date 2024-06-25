from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
import json
from friends.models import Friendship
from lectures.models import Lecture, LectureAttendance
from coins.models import Transaction
from django.conf import settings
from shop.models import Purchase


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
            elif 'event_id' in data:
                # Обработка подтверждения участия в событии
                return handle_doscam_request(request, data['id'])
            else:
                return JsonResponse({'status': 'error', 'message': 'Unknown QR data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid QR data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def handle_friend_request(request, user_id):
    # Логика обработки запроса на добавление в друзья
    # Например:
    from accounts.models import User
    from friends.models import FriendRequest

    to_user = get_object_or_404(User, id=user_id)
    from_user = request.user

    if not Friendship.objects.filter(user1=from_user, user2=to_user).exists() and \
            not Friendship.objects.filter(user1=to_user, user2=from_user).exists():
        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return JsonResponse({'status': 'ok', 'message': 'Friend request sent successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are already friends or request is pending'}, status=400)


def handle_lecture_start(request, lecture_id):
    # Логика обработки начала лекции
    user = request.user
    lecture = get_object_or_404(Lecture, id=lecture_id)

    attendance, created = LectureAttendance.objects.get_or_create(user=user, lecture=lecture)
    if attendance.start_scanned:
        return JsonResponse(
            {'status': 'error', 'message': 'You have already scanned the start QR code for this lecture'}, status=400)

    attendance.start_scanned = True
    attendance.start_time = timezone.now()
    attendance.save()

    return JsonResponse({'status': 'ok', 'message': 'Lecture start handled successfully'})


def handle_lecture_end(request, lecture_id):
    # Логика обработки окончания лекции
    user = request.user
    lecture = get_object_or_404(Lecture, id=lecture_id)

    attendance = LectureAttendance.objects.filter(user=user, lecture=lecture).first()
    if not attendance or not attendance.start_scanned:
        return JsonResponse({'status': 'error', 'message': 'You need to scan the start QR code first'}, status=400)

    if attendance.end_scanned:
        return JsonResponse({'status': 'error', 'message': 'You have already scanned the end QR code for this lecture'},
                            status=400)

    attendance.end_scanned = True
    attendance.end_time = timezone.now()
    attendance.save()

    reward_amount = settings.LECTURE_REWARD_COINS

    Transaction.objects.create(
        sender=user,
        recipient=user,
        amount=reward_amount,
        description=f'Reward for attending lecture {lecture.title}',
        is_system_transaction=True
    )

    return JsonResponse(
        {'status': 'ok', 'message': f'Lecture end handled successfully and received {reward_amount} coins.'})


def handle_purchase(request, purchase_id):
    # Логика обработки покупки
    user = request.user
    purchase = get_object_or_404(Purchase, id=purchase_id)

    if user.doscointbalance.balance < purchase.amount:
        return JsonResponse({'status': 'error', 'message': 'Insufficient balance to complete the purchase'}, status=400)

    Transaction.objects.create(
        sender=user,
        recipient=purchase.seller,
        amount=purchase.amount,
        description=f'Purchase of {purchase.product.name}',
        is_system_transaction=True
    )
    purchase.is_completed = True
    purchase.buyer = user
    purchase.save()

    return JsonResponse({'status': 'ok', 'message': 'Purchase handled successfully'})


def handle_campaign_vote(request, campaign_id):
    # Логика обработки голосования за кампанию
    from campaigns.models import Campaign
    campaign = get_object_or_404(Campaign, id=campaign_id)
    user = request.user

    if campaign.votes.filter(user=user).exists():
        return JsonResponse({'status': 'error', 'message': 'You have already voted for this campaign'}, status=400)

    campaign.votes.create(user=user)

    reward_amount = settings.VOTE_REWARD_COINS
    Transaction.objects.create(
        sender=user,
        recipient=user,
        amount=reward_amount,
        description=f'Reward for voting for campaign {campaign.name}',
        is_system_transaction=True
    )

    return JsonResponse(
        {'status': 'ok', 'message': f'You voted for {campaign.name} and received {reward_amount} coins.'})

def handle_doscam_request(request, user_id):

        return JsonResponse({'status': 'error', 'message': 'handle_doscam_request'}, status=400)

@login_required
def test_page(request):
    return render(request, 'qr_handler/test_page.html')
