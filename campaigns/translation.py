from modeltranslation.translator import translator, TranslationOptions
from .models import Campaign

class CampaignTranslationOptions(TranslationOptions):
    fields = ('leader_name', 'description', 'city')

translator.register(Campaign, CampaignTranslationOptions)
