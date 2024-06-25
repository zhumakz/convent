from django.contrib import admin

from accounts.models import User
from .models import Event
from django.urls import reverse
from django.utils.html import format_html

class EventAdmin(admin.ModelAdmin):
    list_display = ('participant1', 'participant2', 'start_time', 'end_time', 'location', 'is_completed', 'view_event')
    search_fields = ('participant1__phone_number', 'participant2__phone_number')
    list_filter = ('is_completed', 'start_time', 'end_time')

    def view_event(self, obj):
        return format_html('<a href="{}">View</a>', reverse('event_detail_view', args=[obj.pk]))

    view_event.short_description = "Event Details"

    def save_model(self, request, obj, form, change):
        if not change:  # Only when creating a new event
            participants = User.objects.filter(is_active=True).order_by('?')[:2]
            if len(participants) >= 2:
                obj.participant1 = participants[0]
                obj.participant2 = participants[1]
        super().save_model(request, obj, form, change)

admin.site.register(Event, EventAdmin)
