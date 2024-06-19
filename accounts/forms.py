from django import forms
from .models import User, City
import re

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'name', 'surname', 'age', 'city']

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_regex = re.compile(r'^\+7\d{10}$')
        if not phone_regex.match(phone_number):
            raise forms.ValidationError('Введите правильный номер телефона в формате +77475000795.')
        if not User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Пользователь с таким номером телефона не найден.')
        return phone_number

class VerificationForm(forms.Form):
    sms_code = forms.CharField(max_length=4, min_length=4, required=True, label='SMS Code')

    def clean_sms_code(self):
        sms_code = self.cleaned_data.get('sms_code')
        if not sms_code.isdigit():
            raise forms.ValidationError("SMS код должен содержать только цифры.")
        return sms_code

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'age', 'city', 'profile_picture']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')

        if profile_picture:
            if not profile_picture.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')

            if profile_picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size should not exceed 5MB.')

        return profile_picture
