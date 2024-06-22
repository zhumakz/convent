from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Campaign, Vote
from coins.models import DoscointBalance, Transaction
from django.conf import settings

@login_required
def campaign_list(request):
    campaigns = Campaign.objects.all()
    return render(request, 'campaigns/campaign_list.html', {'campaigns': campaigns})

@login_required
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    user = request.user
    has_voted = Vote.objects.filter(user=user, campaign=campaign).exists()
    return render(request, 'campaigns/campaign_detail.html', {'campaign': campaign, 'has_voted': has_voted})

@login_required
def vote_for_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    user = request.user

    if Vote.objects.filter(campaign=campaign, user=user).exists():
        messages.error(request, 'You have already voted for this campaign.')
        return redirect('campaign_detail', campaign_id=campaign_id)

    Vote.objects.create(campaign=campaign, user=user)

    reward_amount = settings.VOTE_REWARD_COINS

    Transaction.objects.create(
        sender=user,
        recipient=user,
        amount=reward_amount,
        description=f'Reward for voting for campaign {campaign.name}',
        is_system_transaction=True
    )

    messages.success(request, f'You have successfully voted for {campaign.name} and received {reward_amount} coins.')
    return redirect('campaign_detail', campaign_id=campaign_id)

@login_required
def campaign_voters(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    voters = Vote.objects.filter(campaign=campaign).select_related('user')
    return render(request, 'campaigns/campaign_voters.html', {'campaign': campaign, 'voters': voters})
