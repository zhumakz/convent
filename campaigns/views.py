from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import CampaignService

@login_required
def campaign_list(request):
    campaigns = CampaignService.get_campaigns()
    return render(request, 'campaigns/campaign_list.html', {'campaigns': campaigns})

@login_required
def campaign_detail(request, campaign_id):
    campaign = CampaignService.get_campaign_by_id(campaign_id)
    user = request.user
    has_voted = CampaignService.user_has_voted(user, campaign)
    return render(request, 'campaigns/campaign_detail.html', {'campaign': campaign, 'has_voted': has_voted})

@login_required
def vote_for_campaign(request, campaign_id):
    campaign = CampaignService.get_campaign_by_id(campaign_id)
    user = request.user

    try:
        message = CampaignService.vote_for_campaign(user, campaign)
        messages.success(request, message)
    except ValidationError as e:
        messages.error(request, str(e))

    return redirect('campaign_detail', campaign_id=campaign_id)

@login_required
def campaign_voters(request, campaign_id):
    campaign = CampaignService.get_campaign_by_id(campaign_id)
    voters = CampaignService.get_voters_for_campaign(campaign)
    return render(request, 'campaigns/campaign_voters.html', {'campaign': campaign, 'voters': voters})

@login_required
def voted_campaign(request):
    user = request.user
    has_voted = CampaignService.has_voted(user)
    campaign = CampaignService.get_voted_campaign(user) if has_voted else None
    return render(request, 'campaigns/voted_campaign.html', {
        'campaign': campaign,
        'has_voted': has_voted
    })