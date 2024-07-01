from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _, gettext as __
from .models import User, City
import re

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'name', 'surname', 'age', 'city']

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label=_('Phone Number'))

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_regex = re.compile(r'^\+7\d{10}$')
        if not phone_regex.match(phone_number):
            raise forms.ValidationError(_('Введите правильный номер телефона в формате +77475000795.'))
        if not User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(_('Пользователь с таким номером телефона не найден.'))
        return phone_number

class VerificationForm(forms.Form):
    sms_code = forms.CharField(max_length=4, min_length=4, required=True, label=_('SMS Code'))

    def clean_sms_code(self):
        sms_code = self.cleaned_data.get('sms_code')
        if not sms_code.isdigit():
            raise forms.ValidationError(_("SMS код должен содержать только цифры."))
        return sms_code


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture', 'instagram', 'tiktok']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')

        if profile_picture:
            # Проверяем тип файла
            if not profile_picture.content_type.startswith('image'):
                raise forms.ValidationError('Файл должен быть изображением.')

            # Проверяем размер файла
            if profile_picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Размер файла не должен превышать 5MB.')

        return profile_picture

class ModeratorLoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label=_('Phone Number'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))

    def clean(self):
        phone_number = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password')
        user = authenticate(phone_number=phone_number, password=password)
        if not user or not user.groups.filter(name__in=['AddModerators', 'RemoveModerators']).exists():
            raise forms.ValidationError(_("Invalid login or not a moderator."))
        return self.cleaned_data
