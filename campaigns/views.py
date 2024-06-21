from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Campaign, Vote
from accounts.models import User
from coins.models import DoscointBalance, Transaction  # Импортируем модели DoscointBalance и Transaction
from django.conf import settings

@login_required
def campaign_list(request):
    campaigns = Campaign.objects.all()
    return render(request, 'campaigns/campaign_list.html', {'campaigns': campaigns})

@login_required
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    return render(request, 'campaigns/campaign_detail.html', {'campaign': campaign})

@login_required
def vote_for_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    user = request.user

    if Vote.objects.filter(user=user).exists():
        messages.error(request, 'You have already voted for a campaign.')
        return redirect('campaign_list')

    Vote.objects.create(campaign=campaign, user=user)

    # Добавляем фиксированное количество доскойнов за голос
    reward_amount = settings.CAMPAIGN_VOTE_REWARD
    doscoint_balance, created = DoscointBalance.objects.get_or_create(user=user)
    doscoint_balance.balance += reward_amount
    doscoint_balance.total_earned += reward_amount
    doscoint_balance.save()

    messages.success(request, f'You have voted for {campaign.name} and received {reward_amount} coins.')
    return redirect('campaign_list')
