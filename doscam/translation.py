from modeltranslation.translator import translator, TranslationOptions
from .models import Location


class LocationTranslationOptions(TranslationOptions):
    fields = ('name', 'address')


translator.register(Location, LocationTranslationOptions)
