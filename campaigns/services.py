from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.translation import gettext_lazy as _, gettext as __
from django.db import transaction
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
    def get_previous_vote(user):
        return Vote.objects.filter(user=user).select_related('campaign').first()

    @staticmethod
    @transaction.atomic
    def vote_for_campaign(user, campaign):
        if Vote.objects.filter(campaign=campaign, user=user).exists():
            raise ValidationError(__('Вы уже проголосовали за эту кампанию.'))

        Vote.objects.create(campaign=campaign, user=user)

        reward_amount = settings.VOTE_REWARD_COINS
        transaction = CoinService.create_transaction(
            sender=user,
            recipient=user,
            amount=reward_amount,
            description=__('Награда за голосование за кампанию {campaign_name}').format(campaign_name=campaign.name),
            category_name='vote_bonus'
        )

        return transaction, __('Вы успешно проголосовали за {campaign_name} и получили {reward_amount} монет.').format(
            campaign_name=campaign.name, reward_amount=reward_amount)

    @staticmethod
    def get_voters_for_campaign(campaign):
        return Vote.objects.filter(campaign=campaign).select_related('user')
    @staticmethod
    def get_voted_campaign(user):
        vote = Vote.objects.filter(user=user).select_related('campaign').first()
        return vote.campaign if vote else None
    @staticmethod
    def has_voted(user):
        return Vote.objects.filter(user=user).exists()
