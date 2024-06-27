from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import LectureService

@login_required
def lecture_list(request):
    lectures = LectureService.get_lectures()
    return render(request, 'lectures/lecture_list.html', {'lectures': lectures})

@login_required
def lecture_detail(request, lecture_id):
    lecture = LectureService.get_lecture_by_id(lecture_id)
    user = request.user
    attendance = LectureService.get_attendance(user, lecture)
    return render(request, 'lectures/lecture_detail.html', {'lecture': lecture, 'attendance': attendance})

@login_required
def scan_lecture_qr_start(request, lecture_id):
    lecture = LectureService.get_lecture_by_id(lecture_id)
    user = request.user

    success, message = LectureService.register_lecture_start(user, lecture)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect('lecture_detail', lecture_id=lecture_id)

@login_required
def scan_lecture_qr_end(request, lecture_id):
    lecture = LectureService.get_lecture_by_id(lecture_id)
    user = request.user

    success, message = LectureService.register_lecture_end(user, lecture)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect('lecture_detail', lecture_id=lecture_id)
