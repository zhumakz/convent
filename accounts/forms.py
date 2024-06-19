from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'name', 'surname', 'age']

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15)

class VerificationForm(forms.Form):
    sms_code = forms.CharField(max_length=6)
