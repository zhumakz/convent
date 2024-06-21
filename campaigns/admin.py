from django.contrib import admin
from .models import Campaign, Vote

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader_name', 'city')
    search_fields = ('name', 'leader_name', 'city')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'user', 'voted_at')
    search_fields = ('campaign__name', 'user__phone_number')
