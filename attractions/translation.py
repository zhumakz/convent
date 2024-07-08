from modeltranslation.translator import translator, TranslationOptions
from .models import Attraction


class AttractionTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'location')


translator.register(Attraction, AttractionTranslationOptions)
