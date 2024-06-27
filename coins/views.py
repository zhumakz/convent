from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import TransactionForm
from .decorators import add_coins_permission_required, remove_coins_permission_required
from .services import CoinService
import logging

logger = logging.getLogger('coins')

@login_required
def balance_view(request):
    logger.debug(f'Balance view accessed by: {request.user}')
    balance = CoinService.get_balance(request.user)
    transactions = CoinService.get_transactions(request.user).order_by('-timestamp')

    processed_transactions = [CoinService.process_transaction(tx, request.user) for tx in transactions]

    return render(request, 'coins/balance.html', {'balance': balance, 'transactions': processed_transactions})

@login_required
@add_coins_permission_required
def add_coins_view(request):
    logger.debug(f'Add coins view accessed by: {request.user}')
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            try:
                CoinService.create_transaction(
                    sender=request.user,
                    recipient=transaction.recipient,
                    amount=transaction.amount,
                    description=transaction.description
                )
                logger.debug(f'Coins added: {transaction.amount} to {transaction.recipient}')
                return redirect('balance')
            except ValidationError as e:
                form.add_error(None, e.message)
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'coins/add_coins.html', {'form': form})

@login_required
@remove_coins_permission_required
def remove_coins_view(request):
    logger.debug(f'Remove coins view accessed by: {request.user}')
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            try:
                CoinService.create_transaction(
                    sender=request.user,
                    recipient=transaction.recipient,
                    amount=-transaction.amount,  # Отрицательное значение для удаления
                    description=transaction.description
                )
                logger.debug(f'Coins removed: {transaction.amount} from {transaction.recipient}')
                return redirect('balance')
            except ValidationError as e:
                form.add_error(None, e.message)
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'coins/remove_coins.html', {'form': form})

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
