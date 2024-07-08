from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Event, Location
@admin.register(Location)
class LocationAdmin(TranslationAdmin):
    list_display = ('name', 'address',)
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
    )
    search_fields = ('name', 'address',)
    list_filter = ('name',)


class EventAdmin(admin.ModelAdmin):
    list_display = ('participant1', 'participant2', 'location', 'start_time', 'end_time', 'is_completed')
    readonly_fields = ('start_time', 'end_time')


admin.site.register(Event, EventAdmin)
