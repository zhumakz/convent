from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Event, Location


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['duration_minutes']


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address']
