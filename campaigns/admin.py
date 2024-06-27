from django.contrib import admin
from django.utils.translation import gettext_lazy as _, gettext as __
from .models import Campaign, Vote


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader_name', 'city')
    actions = ['generate_qr_codes']

    def generate_qr_codes(self, request, queryset):
        for campaign in queryset:
            campaign.generate_qr_code()
            campaign.save()
        self.message_user(request, __("QR codes generated successfully."))

    generate_qr_codes.short_description = __("Generate QR codes for selected campaigns")


admin.site.register(Campaign, CampaignAdmin)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'user', 'voted_at')
    search_fields = ('campaign__name', 'user__phone_number')
