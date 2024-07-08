from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import PointOfInterest


@admin.register(PointOfInterest)
class PointOfInterestAdmin(TranslationAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'title_ru', 'description', 'description_ru')
    list_filter = ('title',)
