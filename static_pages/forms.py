from django import forms
from .models import StaticPage

class StaticPageForm(forms.ModelForm):
    class Meta:
        model = StaticPage
        fields = ['title', 'description', 'photo']
