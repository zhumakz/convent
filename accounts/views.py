from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _, gettext as __

from campaigns.services import CampaignService
from coins.services import CoinService
from doscam.services import EventService
from friends.services import FriendService
from .forms import RegistrationForm, LoginForm, VerificationForm, ProfileEditForm, ModeratorLoginForm, \
    ProfilePictureForm
from .models import User
from .services import UserService


def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(None)
            user.save()
            return redirect('registration_success')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})


def registration_success_view(request):
    return render(request, 'accounts/registration-success.html')


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
                return JsonResponse({'status': 'error', 'message': __('Пользователь с таким номером телефона не найден.')}, status=400)

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
        return JsonResponse({'status': 'error', 'message': __('Пользователь с таким номером телефона не найден.')}, status=400)

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
            return JsonResponse({'status': 'error', 'message': __('Пользователь с таким номером телефона не найден.')}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': __('Неверный SMS код.')}, status=400)


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

    # Проверка наличия фото профиля один раз за сессию
    if not request.session.get('profile_picture_checked', False):
        if not user.profile_picture:
            request.session['profile_picture_checked'] = True
            return redirect('selfie')

    # Использование кэша для списка друзей
    cache_key_friends = f'user_friends_{user.id}'
    friends = cache.get(cache_key_friends)
    if not friends:
        friends = FriendService.get_friends(user)
        cache.set(cache_key_friends, friends, timeout=300)  # Кэширование на 5 минут

    # Использование кэша для транзакций
    cache_key_transactions = f'user_transactions_{user.id}'
    transactions = cache.get(cache_key_transactions)
    if not transactions:
        transactions = CoinService.get_transactions(user).select_related('sender', 'recipient', 'category').order_by('-timestamp')
        cache.set(cache_key_transactions, transactions, timeout=300)  # Кэширование на 5 минут

    # Добавление названий категорий к транзакциям
    for transaction in transactions:
        transaction.category_display_name = CoinService.get_display_name_by_category_id(transaction.category_id)

    # Использование кэша для текущего события
    cache_key_event = f'current_event_{user.id}'
    current_event = cache.get(cache_key_event)
    if current_event is None:
        current_event = EventService.check_active_event_by_user(user)
        cache.set(cache_key_event, current_event, timeout=300)  # Кэширование на 5 минут

    has_voted = CampaignService.has_voted(user)

    return render(request, 'accounts/profile.html', {
        'user': user,
        'friends': friends,
        'transactions': transactions,
        'has_voted': has_voted,
        'current_event': current_event,
        'is_event_participant': current_event and (
            current_event.participant1 == user or current_event.participant2 == user)
    })

@login_required
def selfie_view(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            request.session['profile_picture_checked'] = False  # Сбросить флаг проверки
            return redirect('profile')

    return render(request, 'accounts/selfie.html', {'form': ProfilePictureForm()})


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Перенаправляем на страницу профиля после успешного сохранения
        else:
            return render(request, 'accounts/profile.html', {'form': form})
    else:
        form = ProfileEditForm(instance=request.user)
        return render(request, 'accounts/profile.html', {'form': form})


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
                if user.groups.filter(name='Главный оператор').exists():
                    return redirect('moderator_dashboard')
                elif user.groups.filter(name='Оператор').exists():
                    return redirect('moderator_dashboard')
                elif user.groups.filter(name='Продавец').exists():
                    return redirect('moderator_dashboard')
                elif user.groups.filter(name='Оператор Doscam').exists():
                    return redirect('moderator_dashboard')
                else:
                    return redirect('profile')
    else:
        form = ModeratorLoginForm()
    return render(request, 'accounts/moderator_login.html', {'form': form})
