from modeltranslation.translator import translator, TranslationOptions
from .models import TransactionCategory


class TransactionCategoryTranslationOptions(TranslationOptions):
    fields = ('display_name',)


translator.register(TransactionCategory, TransactionCategoryTranslationOptions)
