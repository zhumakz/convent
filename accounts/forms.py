from django import forms
from .models import User, City

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'name', 'surname', 'age', 'city']

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15)

class VerificationForm(forms.Form):
    sms_code = forms.CharField(max_length=4)

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
