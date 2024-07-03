from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, gettext as __
from .forms import TransactionForm
from .decorators import add_coins_permission_required, remove_coins_permission_required
from .services import CoinService
import logging

logger = logging.getLogger('coins')

@login_required
def balance_view(request):
    balance = CoinService.get_balance(request.user)
    transactions = CoinService.get_transactions(request.user).select_related('sender', 'recipient').order_by('-timestamp')
    processed_transactions = [CoinService.process_transaction(tx, request.user) for tx in transactions]
    return render(request, 'coins/balance.html', {'balance': balance, 'transactions': processed_transactions})
@login_required
def profile_view(request):
    logger.debug(f'Profile view accessed by: {request.user}')
    if request.user.groups.filter(name='AddModerators').exists():
        return redirect('add_coins')
    elif request.user.groups.filter(name='RemoveModerators').exists():
        return redirect('remove_coins')
    else:
        balance = CoinService.get_balance(request.user)
        total_earned = request.user.doscointbalance.total_earned
        return render(request, 'accounts/profile.html', {'balance': balance, 'total_earned': total_earned})
