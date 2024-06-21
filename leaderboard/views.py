from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from coins.models import DoscointBalance
from accounts.models import User

@login_required
def top_users_view(request):
    top_users = DoscointBalance.objects.filter(
        user__is_admin=False,
        user__groups__name__in=['AddModerators', 'RemoveModerators']
    ).exclude(user__is_superuser=True).order_by('-total_earned')[:10]
    return render(request, 'leaderboard/top_users.html', {'top_users': top_users})
