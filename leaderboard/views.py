from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from campaigns.models import Campaign
from friends.models import Friendship
from accounts.models import User


@login_required
def top_users_view(request):
    top_users = User.objects.annotate(
        num_friends=Count('friendships1') + Count('friendships2')
    ).filter(
        is_admin=False,
        is_superuser=False
    ).order_by('-num_friends')[:10]

    return render(request, 'leaderboard/top_users.html', {'top_users': top_users})


@login_required
def top_campaigns_view(request):
    top_campaigns = Campaign.objects.annotate(num_votes=Count('votes')).order_by('-num_votes')[:5]
    return render(request, 'leaderboard/top_campaigns.html', {'top_campaigns': top_campaigns})
