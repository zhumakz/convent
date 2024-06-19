from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import User
from .forms import RegistrationForm, LoginForm, VerificationForm
import random

def generate_sms_code():
    return str(random.randint(100000, 999999))

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
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                request.session['phone_number'] = phone_number
                request.session['sms_code'] = generate_sms_code()
                print(f"SMS код: {request.session['sms_code']}")  # Убедитесь, что этот код выводится в консоль
                return redirect('login')
            else:
                form.add_error('phone_number', 'Пользователь не найден')
    else:
        form = LoginForm()
    verification_form = VerificationForm()
    return render(request, 'accounts/login.html', {'form': form, 'verification_form': verification_form})

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
                    return redirect('profile')
                else:
                    form.add_error(None, 'Пользователь не найден')
            else:
                form.add_error('sms_code', 'Неправильный SMS код')
    else:
        form = VerificationForm()
    return render(request, 'accounts/verify_login.html', {'form': form})

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/profile.html', {'user': request.user})
