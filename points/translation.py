from modeltranslation.translator import translator, TranslationOptions
from .models import PointOfInterest


class PointOfInterestTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


translator.register(PointOfInterest, PointOfInterestTranslationOptions)
