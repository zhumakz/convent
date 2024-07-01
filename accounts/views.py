from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _, gettext as __

from coins.services import CoinService
from friends.services import FriendService
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


def login_and_verify_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            action = request.POST.get('action')
            phone_number = request.POST.get('phone_number')

            if action == 'resend_sms':
                return handle_resend_sms(request, phone_number)

            if action == 'verify_login':
                return handle_verify_login(request)

            if action == 'send_sms':
                user = UserService.get_user_by_phone_number(phone_number)
                if user:
                    UserService.handle_sms_verification(request, phone_number)
                    request.session['phone_number'] = phone_number
                    request.session['sms_sent'] = True
                    return JsonResponse({'status': 'ok'})
                return JsonResponse({'status': 'error', 'message': __('User not found')}, status=400)

            return JsonResponse({'status': 'error', 'message': __('Invalid action')}, status=400)

        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            user = UserService.get_user_by_phone_number(phone_number)
            if user:
                allowed, remaining_time = UserService.is_sms_verification_allowed(request)
                if not allowed:
                    return render_login_page(request, form, remaining_time)

                UserService.handle_sms_verification(request, phone_number)
                request.session['phone_number'] = phone_number
                request.session['sms_sent'] = True
                return render_login_page(request, form, 60)
        return render_login_page(request, form)
    else:
        form = LoginForm()
        show_popup, remaining_time = get_popup_status(request)
        return render_login_page(request, form, remaining_time, show_popup)


def handle_resend_sms(request, phone_number):
    if not phone_number:
        return JsonResponse({'status': 'error', 'message': __('Phone number is required')}, status=400)

    user = UserService.get_user_by_phone_number(phone_number)
    if not user:
        return JsonResponse({'status': 'error', 'message': __('User not found')}, status=400)

    UserService.handle_sms_verification(request, phone_number)
    return JsonResponse({'status': 'ok'})


def handle_verify_login(request):
    sms_code = request.POST.get('sms_code')
    if sms_code == request.session.get('sms_code'):
        phone_number = request.session.get('phone_number')
        user = UserService.get_user_by_phone_number(phone_number)
        user = authenticate(phone_number=phone_number)
        if user is not None:
            login(request, user)
            request.session['sms_sent'] = False  # Сброс состояния отправки SMS
            return JsonResponse({'status': 'ok', 'redirect_url': reverse('profile')})
        else:
            return JsonResponse({'status': 'error', 'message': __('User not found')}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': __('Incorrect SMS code')}, status=400)


def render_login_page(request, form, remaining_time=None, show_popup=False):
    return render(request, 'accounts/login.html', {
        'form': form,
        'verification_form': VerificationForm(),
        'show_popup': show_popup,
        'remaining_time': remaining_time
    })


def get_popup_status(request):
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
    return show_popup, remaining_time


@login_required
def profile_view(request):
    user = request.user
    friends = FriendService.get_friends(user)
    transactions = CoinService.get_transactions(user).select_related('sender', 'recipient').order_by('-timestamp')
    processed_transactions = [CoinService.process_transaction(tx, user) for tx in transactions]

    return render(request, 'accounts/profile.html', {
        'user': user,
        'friends': friends,
        'transactions': processed_transactions,
    })


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
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
