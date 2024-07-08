from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Attraction

@admin.register(Attraction)
class AttractionAdmin(TranslationAdmin):
    list_display = ('title', 'description', 'location', 'start_time', 'end_time')
    search_fields = ('title', 'title_ru', 'description', 'description_ru', 'location', 'location_ru')
    list_filter = ('title',)
