from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Event, Location


class EventForm(forms.ModelForm):
    min_friends = forms.IntegerField(required=False, label=_("Minimum number of friends"))
    has_profile_picture = forms.BooleanField(required=False, label=_("Has profile picture"))

    class Meta:
        model = Event
        fields = ['location', 'duration_minutes']


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address']
