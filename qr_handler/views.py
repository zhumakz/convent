from django.core.exceptions import ValidationError
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
def test_page(request):
    return render(request, 'qr_handler/test_page.html')
@login_required
def qr_scan_view(request):
    # Отображение страницы с формой для сканирования QR-кода
    return render(request, 'qr_handler/qr.html')
#
# @login_required
# def handle_qr_data(request):
#     if request.method == 'POST':
#         qr_data = request.POST.get('qr_data')
#         if qr_data:
#             try:
#                 data = json.loads(qr_data)
#                 user_id = data.get('user_id')
#                 lecture_start = data.get('lecture_start')
#                 lecture_end = data.get('lecture_end')
#                 purchase_id = data.get('purchase_id')
#                 campaign_vote = data.get('campaign_vote')
#
#                 # Логика перенаправления в зависимости от данных QR-кода
#                 if user_id:
#                     return redirect('qr_friend_request')
#                 elif purchase_id:
#                     return redirect('qr_purchase_detail', purchase_id=purchase_id)
#                 elif campaign_vote:
#                     return redirect('qr_campaign_vote', campaign_vote=campaign_vote)
#                 elif lecture_start and lecture_end:
#                     return redirect('qr_lecture_detail', lecture_start=lecture_start, lecture_end=lecture_end)
#                 else:
#                     return redirect('profile')
#
#             except json.JSONDecodeError:
#                 # Обработка ошибки декодирования JSON
#                 return JsonResponse({'error': 'Invalid QR data'}, status=400)
#
#     return redirect('profile')
#
# def handle_friend_request(request, user_id):
#     try:
#         to_user = get_object_or_404(User, id=user_id)
#         from_user = request.user
#
#         if from_user == to_user:
#             logger.warning("User tried to add themselves as a friend")
#             message = 'You cannot add yourself as a friend.'
#             return redirect('operation_error', message=message)
#
#         if to_user.is_admin or to_user.is_moderator:
#             logger.warning("User tried to add an admin or moderator as a friend")
#             message = 'You cannot add administrators or moderators as friends.'
#             return redirect('operation_error', message=message)
#
#         if FriendService.are_friends(from_user, to_user):
#             logger.warning("Users are already friends")
#             message = 'You are already friends.'
#             return redirect('operation_error', message=message)
#
#         friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user).first()
#
#         if friend_request:
#             message = FriendService.confirm_friend_request(friend_request)
#
#         else:
#             if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
#                 logger.warning("Friend request already sent")
#                 message = 'Friend request already sent.'
#                 return redirect('operation_error', message=message)
#
#             success, message = FriendService.send_friend_request(from_user, to_user)
#
#         return render(request, 'qr_handler/friend_request_success.html')
#
#     except Exception as e:
#         logger.error("Error handling friend request: %s", e, exc_info=True)
#         return redirect('operation_error', message=str(e))
#
#
# def handle_lecture_start(request, lecture_id):
#     try:
#         user = request.user
#         lecture = get_object_or_404(Lecture, id=lecture_id)
#
#         success, message = LectureService.register_lecture_start(user, lecture)
#         if success:
#             return JsonResponse({'status': 'ok', 'message': message})
#         else:
#             message = 'Friend request already sent.'
#             return redirect('operation_error', message=message)
#     except Exception as e:
#         logger.error("Error handling lecture start: %s", e, exc_info=True)
#         return redirect('operation_error', message=str(e))
#
#
# def handle_lecture_end(request, lecture_id):
#     try:
#         user = request.user
#         lecture = get_object_or_404(Lecture, id=lecture_id)
#
#         success, message = LectureService.register_lecture_end(user, lecture)
#         if success:
#             return JsonResponse({'status': 'ok', 'message': message})
#         else:
#             return JsonResponse({'status': 'error', 'message': message})
#     except Exception as e:
#         logger.error("Error handling lecture end: %s", e, exc_info=True)
#         return redirect('operation_error', message=str(e))
#
#
# def handle_purchase(request, purchase_id):
#     try:
#         user = request.user
#         purchase = get_object_or_404(Purchase, id=purchase_id)
#
#         if user.doscointbalance.balance < purchase.amount:
#             logger.warning("Insufficient balance to complete the purchase")
#             return JsonResponse({'status': 'error', 'message': 'Insufficient balance to complete the purchase'})
#
#         Transaction.objects.create(
#             sender=user,
#             recipient=purchase.seller,
#             amount=purchase.amount,
#             description=f'Purchase of {purchase.product.name}',
#             is_system_transaction=True
#         )
#         purchase.is_completed = True
#         purchase.buyer = user
#         purchase.save()
#
#         return JsonResponse({'status': 'ok', 'message': 'Purchase handled successfully'})
#     except Exception as e:
#         logger.error("Error handling purchase: %s", e, exc_info=True)
#         return redirect('operation_error', message=str(e))
#
#
# def handle_doscam_request(request, user_id):
#     try:
#         return JsonResponse({'status': 'error', 'message': 'handle_doscam_request'})
#     except Exception as e:
#         logger.error("Error handling event request: %s", e, exc_info=True)
#         return redirect('operation_error', message=str(e))
#
#

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
                elif lecture_start and lecture_end:
                    return redirect('qr_lecture_detail')
                else:
                    return redirect('profile')

            except json.JSONDecodeError:
                # Обработка ошибки декодирования JSON
                return JsonResponse({'error': 'Invalid QR data'}, status=400)

    return redirect('qr_handler:profile')

@login_required
def qr_friend_request(request):
    data = request.session.get('qr_data')
    if not data:
        return redirect('profile')

    user_id = data.get('user_id')

    try:
        to_user = User.objects.get(id=user_id)
        success, message = FriendService.send_friend_request(request.user, to_user)
        context = {
            'message': message,
            'success': success,
            'to_user': to_user,
            'qr_code_url': request.user.qr_code.url
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
def qr_purchase_detail(request, purchase_id):
    # Логика для отображения информации о покупке по QR-коду
    context = {'purchase_id': purchase_id}
    return render(request, 'qr_handler/qr_purchase_detail.html', context)

@login_required
def qr_campaign_vote(request, campaign_vote):
    # Логика для обработки голосования в кампании по QR-коду
    context = {'campaign_vote': campaign_vote}
    return render(request, 'qr_handler/qr_campaign_vote.html', context)

@login_required
def qr_lecture_detail(request, lecture_start, lecture_end):
    # Логика для отображения информации о лекции по QR-коду
    context = {'lecture_start': lecture_start, 'lecture_end': lecture_end}
    return render(request, 'qr_handler/qr_lecture_detail.html', context)