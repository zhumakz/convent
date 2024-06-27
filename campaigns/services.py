from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, gettext as __
from .models import Campaign, Vote
from coins.services import CoinService
from django.core.exceptions import ValidationError


class CampaignService:

    @staticmethod
    def get_campaigns():
        return Campaign.objects.all()

    @staticmethod
    def get_campaign_by_id(campaign_id):
        return get_object_or_404(Campaign, id=campaign_id)

    @staticmethod
    def user_has_voted(user, campaign):
        return Vote.objects.filter(user=user, campaign=campaign).exists()

    @staticmethod
    def vote_for_campaign(user, campaign):
        if Vote.objects.filter(campaign=campaign, user=user).exists():
            raise ValidationError(__('You have already voted for this campaign.'))

        Vote.objects.create(campaign=campaign, user=user)

        reward_amount = settings.VOTE_REWARD_COINS
        CoinService.create_transaction(
            sender=user,
            recipient=user,
            amount=reward_amount,
            description=__('Reward for voting for campaign {campaign_name}').format(campaign_name=campaign.name),
            is_system_transaction=True
        )

        return __('You have successfully voted for {campaign_name} and received {reward_amount} coins.').format(
            campaign_name=campaign.name, reward_amount=reward_amount)

    @staticmethod
    def get_voters_for_campaign(campaign):
        return Vote.objects.filter(campaign=campaign).select_related('user')
