from django.contrib import admin
from .models import Attraction

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'location')
    search_fields = ('title', 'description', 'location')
    list_filter = ('start_time', 'end_time', 'location')
