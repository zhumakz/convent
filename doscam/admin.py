from django.contrib import admin
from .models import Event, Location


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')


class EventAdmin(admin.ModelAdmin):
    list_display = ('participant1', 'participant2', 'location', 'start_time', 'end_time', 'is_completed')
    readonly_fields = ('start_time', 'end_time')


admin.site.register(Event, EventAdmin)
admin.site.register(Location, LocationAdmin)
