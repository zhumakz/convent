from django import forms
from .models import Attraction

class AttractionForm(forms.ModelForm):
    class Meta:
        model = Attraction
        fields = ['title', 'description', 'photo', 'start_time', 'end_time', 'location']
