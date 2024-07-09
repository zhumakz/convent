from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, gettext as __
from .models import User, City
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import re


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'name', 'surname', 'age', 'city']
        widgets = {
            'phone_number': forms.TextInput(
                attrs={'class': 'register__input', 'placeholder': '+7 (777) 000-00-00', 'inputmode': 'tel',
                       'value': ''}),
            'name': forms.TextInput(attrs={'class': 'register__item-input'}),
            'surname': forms.TextInput(attrs={'class': 'register__item-input'}),
            'age': forms.NumberInput(attrs={'class': 'register__input', 'pattern': '[0-9]*', 'inputmode': 'numeric'}),
            'city': forms.Select(attrs={'class': 'register__select'}),
        }
        labels = {
            'phone_number': _('Номер телефона'),
            'name': _('Имя'),
            'surname': _('Фамилия'),
            'age': _('Возраст'),
            'city': _('Город'),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_regex = re.compile(r'^\+7\d{10}$')
        if not phone_regex.match(phone_number):
            raise forms.ValidationError(_('Введите правильный номер телефона в формате +77475000795.'))
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(_('Пользователь с таким номером телефона уже зарегистрирован.'))
        return phone_number

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 16:
            raise forms.ValidationError(_("Возраст должен быть не менее 16 лет"))
        return age

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.isalpha():
            raise forms.ValidationError(_("Имя должно содержать только буквы"))
        return name

    def clean_surname(self):
        surname = self.cleaned_data.get('surname')
        if not surname.isalpha():
            raise forms.ValidationError(_("Фамилия должна содержать только буквы"))
        return surname


class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label=_('Phone Number'))

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_regex = re.compile(r'^\+7\d{10}$')
        if not phone_regex.match(phone_number):
            raise forms.ValidationError(_('Введите правильный номер телефона в формате +77475000795.'))
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise forms.ValidationError(_('Пользователь с таким номером телефона не найден.'))

        if not user.is_active:
            raise forms.ValidationError(_('Этот пользователь не активирован.'))

        return phone_number


class VerificationForm(forms.Form):
    sms_code = forms.CharField(max_length=4, min_length=4, required=True, label=_('SMS Code'))

    def clean_sms_code(self):
        sms_code = self.cleaned_data.get('sms_code')
        if not sms_code.isdigit():
            raise forms.ValidationError(_("SMS код должен содержать только цифры."))
        return sms_code


def process_profile_picture(profile_picture):
    if profile_picture:
        # Открываем изображение и проверяем его формат
        try:
            img = Image.open(profile_picture)
            img.verify()  # Проверяем, является ли файл изображением
            img = Image.open(profile_picture)  # Открываем заново, так как verify() закрывает файл
        except (IOError, SyntaxError):
            raise forms.ValidationError('Файл должен быть изображением.')

        # Проверка размера файла
        if profile_picture.size > 10 * 1024 * 1024:
            raise forms.ValidationError('Размер файла не должен превышать 10MB.')

        # Обрезка изображения
        if img.width > 512:
            # Сохранение пропорций
            aspect_ratio = img.height / img.width
            new_height = int(512 * aspect_ratio)
            img = img.resize((512, new_height), Image.LANCZOS)  # Использование Image.LANCZOS вместо Image.ANTIALIAS

            # Сохранение обрезанного изображения в BytesIO
            output = BytesIO()
            img.save(output, format='JPEG')
            output.seek(0)

            # Создание нового InMemoryUploadedFile для обновления profile_picture
            profile_picture = InMemoryUploadedFile(output, 'ImageField', profile_picture.name, 'image/jpeg',
                                                   output.getbuffer().nbytes, None)

    return profile_picture


def process_profile_pictureSelfie(profile_picture):
    if profile_picture:
        # Открываем изображение и проверяем его формат
        try:
            img = Image.open(profile_picture)
            img.verify()  # Проверяем, является ли файл изображением
            img = Image.open(profile_picture)  # Открываем заново, так как verify() закрывает файл
        except (IOError, SyntaxError):
            raise forms.ValidationError('Файл должен быть изображением.')

        # Проверка размера файла
        if profile_picture.size > 10 * 1024 * 1024:
            raise forms.ValidationError('Размер файла не должен превышать 10MB.')

        # Обрезка изображения
        if img.width > 512:
            # Сохранение пропорций
            aspect_ratio = img.height / img.width
            new_height = int(512 * aspect_ratio)
            img = img.resize((512, new_height), Image.LANCZOS)  # Использование Image.LANCZOS вместо Image.ANTIALIAS

            # Сохранение обрезанного изображения в BytesIO
            output = BytesIO()
            img.save(output, format='JPEG')
            output.seek(0)

            # Создание нового InMemoryUploadedFile для обновления profile_picture
            profile_picture = InMemoryUploadedFile(output, 'ImageField', profile_picture.name, 'image/jpeg',
                                                   output.getbuffer().nbytes, None)

    return profile_picture


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture', 'instagram', 'tiktok']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        return process_profile_picture(profile_picture)


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']

    def process_profile_pictureSelfie(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        return process_profile_picture(profile_picture)


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
