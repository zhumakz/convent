from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.dateformat import format
from django.views.decorators.csrf import csrf_exempt

from convent import settings
from .models import User
from .forms import RegistrationForm, LoginForm, VerificationForm, ProfileEditForm
import random
from utils.sms import send_sms


def generate_sms_code():
    return str(random.randint(1000, 9999))


def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(None)
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            phone_number = request.POST.get('phone_number')
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                sms_code = generate_sms_code()
                request.session['phone_number'] = phone_number
                request.session['sms_code'] = sms_code
                request.session['sms_sent'] = True
                request.session['last_sms_time'] = format(timezone.now(), 'Y-m-d H:i:s')
                message = f"{settings.SMS_VERIFICATION_MESSAGE} {sms_code}"
                if send_sms(phone_number, message):
                    return JsonResponse({'status': 'ok'})
            return JsonResponse({'status': 'error'}, status=400)

        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                last_sms_time_str = request.session.get('last_sms_time')
                if last_sms_time_str:
                    last_sms_time = timezone.make_aware(parse_datetime(last_sms_time_str))
                    time_diff = timezone.now() - last_sms_time
                    if time_diff.total_seconds() < 60:
                        remaining_time = 60 - int(time_diff.total_seconds())
                        return render(request, 'accounts/login.html', {
                            'form': form,
                            'verification_form': VerificationForm(),
                            'show_popup': True,
                            'remaining_time': remaining_time
                        })

                sms_code = generate_sms_code()
                request.session['phone_number'] = phone_number
                request.session['sms_code'] = sms_code
                request.session['sms_sent'] = True
                request.session['last_sms_time'] = format(timezone.now(), 'Y-m-d H:i:s')
                message = f"{settings.SMS_VERIFICATION_MESSAGE}  {sms_code}"
                if send_sms(phone_number, message):
                    print(f"SMS code sent: {sms_code}")
                return render(request, 'accounts/login.html',
                              {'form': form, 'verification_form': VerificationForm(), 'show_popup': True,
                               'remaining_time': 60})
        return render(request, 'accounts/login.html', {'form': form, 'show_popup': False})
    else:
        form = LoginForm()
        show_popup = request.session.get('sms_sent', False)
        last_sms_time_str = request.session.get('last_sms_time')
        if show_popup and last_sms_time_str:
            last_sms_time = timezone.make_aware(parse_datetime(last_sms_time_str))
            remaining_time = 60 - (timezone.now() - last_sms_time).total_seconds()
            if remaining_time < 0:
                remaining_time = None
                show_popup = False
        else:
            remaining_time = None
        return render(request, 'accounts/login.html',
                      {'form': form, 'verification_form': VerificationForm(), 'show_popup': show_popup,
                       'remaining_time': remaining_time})


@csrf_exempt
def resend_sms_view(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            return JsonResponse({'status': 'error', 'message': 'Phone number is required'}, status=400)

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=400)

        sms_code = generate_sms_code()
        request.session['sms_code'] = sms_code
        request.session['sms_sent'] = True
        request.session['last_sms_time'] = format(timezone.now(), 'Y-m-d H:i:s')
        message = f"Your verification code is {sms_code}"

        if send_sms(phone_number, message):
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to send SMS'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def verify_login_view(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            sms_code = form.cleaned_data['sms_code']
            if sms_code == request.session.get('sms_code'):
                phone_number = request.session.get('phone_number')
                user = User.objects.get(phone_number=phone_number)
                user = authenticate(phone_number=phone_number)
                if user is not None:
                    login(request, user)
                    request.session['sms_sent'] = False  # Сброс состояния отправки SMS
                    return redirect('profile')
                else:
                    form.add_error(None, 'Пользователь не найден')
            else:
                form.add_error('sms_code', 'Неправильный SMS код')
    else:
        form = VerificationForm()
    return render(request, 'accounts/verify_login.html', {'form': form})


@login_required
def profile_view(request):
    form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'user': request.user, 'form': form})


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    return redirect('profile')


@login_required
def user_profile_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'accounts/user_profile.html', {'user': user})


def logout_view(request):
    logout(request)
    return redirect('login')
