from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _, gettext as __

from .forms import RegistrationForm, LoginForm, VerificationForm, ProfileEditForm, ModeratorLoginForm
from .models import User
from .services import UserService


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
            user = UserService.get_user_by_phone_number(phone_number)
            if user:
                UserService.handle_sms_verification(request, phone_number)
                return JsonResponse({'status': 'ok'})
            return JsonResponse({'status': 'error', 'message': __('User not found')}, status=400)

        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            user = UserService.get_user_by_phone_number(phone_number)
            if user:
                allowed, remaining_time = UserService.is_sms_verification_allowed(request)
                if not allowed:
                    return render(request, 'accounts/login.html', {
                        'form': form,
                        'verification_form': VerificationForm(),
                        'show_popup': True,
                        'remaining_time': remaining_time
                    })

                UserService.handle_sms_verification(request, phone_number)
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
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            return JsonResponse({'status': 'error', 'message': __('Phone number is required')}, status=400)

        user = UserService.get_user_by_phone_number(phone_number)
        if not user:
            return JsonResponse({'status': 'error', 'message': __('User not found')}, status=400)

        UserService.handle_sms_verification(request, phone_number)
        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'error', 'message': __('Invalid request')}, status=400)


def verify_login_view(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            sms_code = form.cleaned_data['sms_code']
            if sms_code == request.session.get('sms_code'):
                phone_number = request.session.get('phone_number')
                user = UserService.get_user_by_phone_number(phone_number)
                user = authenticate(phone_number=phone_number)
                if user is not None:
                    login(request, user)
                    request.session['sms_sent'] = False  # Сброс состояния отправки SMS
                    return redirect('profile')
                else:
                    form.add_error(None, __('User not found'))
            else:
                form.add_error('sms_code', __('Incorrect SMS code'))
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


def moderator_login_view(request):
    if request.method == 'POST':
        form = ModeratorLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password')
            user = authenticate(phone_number=phone_number, password=password)
            if user is not None:
                login(request, user)
                if user.groups.filter(name='AddModerators').exists():
                    return redirect('add_coins')
                elif user.groups.filter(name='RemoveModerators').exists():
                    return redirect('remove_coins')
                else:
                    return redirect('profile')
    else:
        form = ModeratorLoginForm()
    return render(request, 'accounts/moderator_login.html', {'form': form})
