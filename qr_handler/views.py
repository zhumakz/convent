from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
import json
from friends.models import FriendRequest, Friendship
from lectures.models import Lecture, LectureAttendance
from coins.models import Transaction
from django.conf import settings
from shop.models import Purchase
from accounts.models import User
from friends.services import FriendService
import logging

logger = logging.getLogger(__name__)


@login_required
def qr_scan_view(request):
    return render(request, 'qr_handler/qr.html')


@login_required
def handle_qr_data(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data')
        try:
            data = json.loads(qr_data)
            if 'user_id' in data:
                return handle_friend_request(request, data['user_id'])
            elif 'lecture_start' in data:
                return handle_lecture_start(request, data['lecture_start'])
            elif 'lecture_end' in data:
                return handle_lecture_end(request, data['lecture_end'])
            elif 'purchase_id' in data:
                return handle_purchase(request, data['purchase_id'])
            elif 'event_id' in data:
                return handle_doscam_request(request, data['id'])
            else:
                return JsonResponse({'status': 'error', 'message': 'Unknown QR data'}, status=400)
        except json.JSONDecodeError:
            logger.error("Invalid QR data: %s", qr_data)
            return JsonResponse({'status': 'error', 'message': 'Invalid QR data'}, status=400)
        except Exception as e:
            logger.error("Error handling QR data: %s", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def handle_friend_request(request, user_id):
    try:
        to_user = get_object_or_404(User, id=user_id)
        from_user = request.user

        # Проверка на попытку добавления самого себя
        if from_user == to_user:
            return JsonResponse({'status': 'error', 'message': 'You cannot add yourself as a friend.'}, status=400)

        # Проверка на попытку добавления администратора или модератора
        if to_user.is_admin or to_user.is_moderator:
            return JsonResponse({'status': 'error', 'message': 'You cannot add administrators or moderators as friends.'}, status=400)

        are_friends = FriendService.are_friends(from_user, to_user)

        if are_friends:
            return JsonResponse({'status': 'error', 'message': 'You are already friends'}, status=400)

        friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user).first()

        if friend_request:
            # Confirm friend request
            message = FriendService.confirm_friend_request(friend_request)
            popup_index = 3
        else:
            # Check if there's an existing request to avoid duplicates
            existing_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists()
            if existing_request:
                return JsonResponse({'status': 'error', 'message': 'Friend request already sent'}, status=400)

            # Send friend request
            success, message = FriendService.send_friend_request(from_user, to_user)
            popup_index = 2 if not success else 3

        return JsonResponse({
            'status': 'ok',
            'message': message,
            'popup_index': popup_index,
            'user_info': {
                'name': f"{to_user.name} {to_user.surname}",
                'location': to_user.city.name if to_user.city else '',
                'profile_picture': to_user.profile_picture.url if to_user.profile_picture else None,
                'qr_code': from_user.qr_code.url if from_user.qr_code else None
            }
        })
    except Exception as e:
        logger.error("Error handling friend request: %s", e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



def handle_lecture_start(request, lecture_id):
    try:
        user = request.user
        lecture = get_object_or_404(Lecture, id=lecture_id)

        attendance, created = LectureAttendance.objects.get_or_create(user=user, lecture=lecture)
        if attendance.start_scanned:
            return JsonResponse(
                {'status': 'error', 'message': 'You have already scanned the start QR code for this lecture'},
                status=400)

        attendance.start_scanned = True
        attendance.start_time = timezone.now()
        attendance.save()

        return JsonResponse({'status': 'ok', 'message': 'Lecture start handled successfully'})
    except Exception as e:
        logger.error("Error handling lecture start: %s", e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_lecture_end(request, lecture_id):
    try:
        user = request.user
        lecture = get_object_or_404(Lecture, id=lecture_id)

        attendance = LectureAttendance.objects.filter(user=user, lecture=lecture).first()
        if not attendance or not attendance.start_scanned:
            return JsonResponse({'status': 'error', 'message': 'You need to scan the start QR code first'}, status=400)

        if attendance.end_scanned:
            return JsonResponse(
                {'status': 'error', 'message': 'You have already scanned the end QR code for this lecture'},
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
    except Exception as e:
        logger.error("Error handling lecture end: %s", e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_purchase(request, purchase_id):
    try:
        user = request.user
        purchase = get_object_or_404(Purchase, id=purchase_id)

        if user.doscointbalance.balance < purchase.amount:
            return JsonResponse({'status': 'error', 'message': 'Insufficient balance to complete the purchase'},
                                status=400)

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
    except Exception as e:
        logger.error("Error handling purchase: %s", e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_campaign_vote(request, campaign_id):
    try:
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
    except Exception as e:
        logger.error("Error handling campaign vote: %s", e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_doscam_request(request, user_id):
    try:
        # Логика обработки подтверждения участия в событии
        return JsonResponse({'status': 'error', 'message': 'handle_doscam_request'}, status=400)
    except Exception as e:
        logger.error("Error handling doscam request: %s", e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def test_page(request):
    return render(request, 'qr_handler/test_page.html')
