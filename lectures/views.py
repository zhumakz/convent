from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lecture, LectureAttendance
from django.utils import timezone
from coins.models import DoscointBalance, Transaction
from django.conf import settings

@login_required
def lecture_list(request):
    lectures = Lecture.objects.all()
    return render(request, 'lectures/lecture_list.html', {'lectures': lectures})

@login_required
def lecture_detail(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    user = request.user
    attendance = LectureAttendance.objects.filter(user=user, lecture=lecture).first()
    return render(request, 'lectures/lecture_detail.html', {'lecture': lecture, 'attendance': attendance})

@login_required
def scan_lecture_qr_start(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    user = request.user

    attendance, created = LectureAttendance.objects.get_or_create(user=user, lecture=lecture)
    if attendance.start_scanned:
        messages.error(request, 'You have already scanned the start QR code for this lecture.')
        return redirect('lecture_detail', lecture_id=lecture_id)

    attendance.start_scanned = True
    attendance.start_time = timezone.now()
    attendance.save()

    messages.success(request, 'You have successfully registered for the lecture.')
    return redirect('lecture_detail', lecture_id=lecture_id)

@login_required
def scan_lecture_qr_end(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    user = request.user

    attendance = LectureAttendance.objects.filter(user=user, lecture=lecture).first()
    if not attendance or not attendance.start_scanned:
        messages.error(request, 'You need to scan the start QR code first.')
        return redirect('lecture_detail', lecture_id=lecture_id)

    if attendance.end_scanned:
        messages.error(request, 'You have already scanned the end QR code for this lecture.')
        return redirect('lecture_detail', lecture_id=lecture_id)

    attendance.end_scanned = True
    attendance.end_time = timezone.now()
    attendance.save()

    reward_amount = settings.LECTURE_REWARD_COINS
    doscoint_balance, created = DoscointBalance.objects.get_or_create(user=user)
    doscoint_balance.balance += reward_amount
    doscoint_balance.total_earned += reward_amount
    doscoint_balance.save()

    Transaction.objects.create(
        sender=user,
        recipient=user,
        amount=reward_amount,
        description=f'Reward for attending lecture {lecture.title}',
        is_system_transaction=True
    )

    messages.success(request, f'You have successfully completed the lecture and received {reward_amount} coins.')
    return redirect('lecture_detail', lecture_id=lecture_id)
