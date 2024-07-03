from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from friends.models import FriendRequest
from lectures.models import Lecture
from coins.models import Transaction
from accounts.models import User
from friends.services import FriendService
import logging

from lectures.services import LectureService
from shop.models import Purchase

logger = logging.getLogger(__name__)


@login_required
def qr_scan_view(request):
    return render(request, 'qr_handler/qr.html')


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

            handlers = {
                'user_id': handle_friend_request,
                'lecture_start': handle_lecture_start,
                'lecture_end': handle_lecture_end,
                'purchase_id': handle_purchase,
                'event_id': handle_doscam_request
            }

            for key, handler in handlers.items():
                if key in data:
                    return handler(request, data[key])

            return JsonResponse({'status': 'error', 'message': 'Unknown QR data'})

        except json.JSONDecodeError:
            logger.error("Invalid QR data: %s", qr_data)
            return JsonResponse({'status': 'error', 'message': 'Invalid QR data'})
        except Exception as e:
            logger.error("Error handling QR data: %s", e, exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def handle_friend_request(request, user_id):
    try:
        to_user = get_object_or_404(User, id=user_id)
        from_user = request.user

        if from_user == to_user:
            logger.warning("User tried to add themselves as a friend")
            message = 'You cannot add yourself as a friend.'
            return redirect('operation_error', message=message)

        if to_user.is_admin or to_user.is_moderator:
            logger.warning("User tried to add an admin or moderator as a friend")
            message = 'You cannot add administrators or moderators as friends.'
            return redirect('operation_error', message=message)

        if FriendService.are_friends(from_user, to_user):
            logger.warning("Users are already friends")
            message = 'You are already friends.'
            return redirect('operation_error', message=message)

        friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user).first()

        if friend_request:
            message = FriendService.confirm_friend_request(friend_request)

        else:
            if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
                logger.warning("Friend request already sent")
                message = 'Friend request already sent.'
                return redirect('operation_error', message=message)

            success, message = FriendService.send_friend_request(from_user, to_user)

        request.session['friend_request_data'] = {
            'status': 'ok',
            'message': 'Friend request sent successfully!',
            'user_info': {
                'name': f"{to_user.name} {to_user.surname}",
                'location': to_user.city.name if to_user.city else '',
                'profile_picture': to_user.profile_picture.url if to_user.profile_picture else None,
                'qr_code': to_user.qr_code.url if to_user.qr_code else None
            }
        }
        return redirect('friend_request_success')


    except Exception as e:
        logger.error("Error handling friend request: %s", e, exc_info=True)
        return redirect('operation_error', message=str(e))


def handle_lecture_start(request, lecture_id):
    try:
        user = request.user
        lecture = get_object_or_404(Lecture, id=lecture_id)

        success, message = LectureService.register_lecture_start(user, lecture)
        if success:
            return JsonResponse({'status': 'ok', 'message': message})
        else:
            message = 'Friend request already sent.'
            return redirect('operation_error', message=message)
    except Exception as e:
        logger.error("Error handling lecture start: %s", e, exc_info=True)
        return redirect('operation_error', message=str(e))


def handle_lecture_end(request, lecture_id):
    try:
        user = request.user
        lecture = get_object_or_404(Lecture, id=lecture_id)

        success, message = LectureService.register_lecture_end(user, lecture)
        if success:
            return JsonResponse({'status': 'ok', 'message': message})
        else:
            return JsonResponse({'status': 'error', 'message': message})
    except Exception as e:
        logger.error("Error handling lecture end: %s", e, exc_info=True)
        return redirect('operation_error', message=str(e))


def handle_purchase(request, purchase_id):
    try:
        user = request.user
        purchase = get_object_or_404(Purchase, id=purchase_id)

        if user.doscointbalance.balance < purchase.amount:
            logger.warning("Insufficient balance to complete the purchase")
            return JsonResponse({'status': 'error', 'message': 'Insufficient balance to complete the purchase'})

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
        logger.error("Error handling purchase: %s", e, exc_info=True)
        return redirect('operation_error', message=str(e))


def handle_doscam_request(request, user_id):
    try:
        return JsonResponse({'status': 'error', 'message': 'handle_doscam_request'})
    except Exception as e:
        logger.error("Error handling event request: %s", e, exc_info=True)
        return redirect('operation_error', message=str(e))


@login_required
def test_page(request):
    return render(request, 'qr_handler/test_page.html')


def operation_error(request, message):
    return render(request, 'qr_handler/operation_error.html', {'message': message})


def friend_request_success(request):
    friend_request_data = request.session.pop('friend_request_data', None)
    if friend_request_data:
        return render(request, 'qr_handler/friend_request_success.html', friend_request_data)
    else:
        # Если данных нет в сессии, обработка ошибки
        return redirect('operation_error', message='Data not found')
