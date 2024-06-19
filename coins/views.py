from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from .models import DoscointBalance, Transaction
from .forms import TransactionForm

User = get_user_model()

def user_can_add_coins(user):
    return user.is_authenticated and user.has_perm('coins.can_add_coins')

def user_can_remove_coins(user):
    return user.is_authenticated and user.has_perm('coins.can_remove_coins')

@login_required
def balance_view(request):
    balance = request.user.doscointbalance.balance
    transactions = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(recipient=request.user)
    transactions = transactions.order_by('-timestamp')
    return render(request, 'coins/balance.html', {'balance': balance, 'transactions': transactions})

@login_required
@user_passes_test(user_can_add_coins, login_url='/login/')
def add_coins_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.sender = request.user
            transaction.save()
            return redirect('balance')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'coins/add_coins.html', {'form': form})

@login_required
@user_passes_test(user_can_remove_coins, login_url='/login/')
def remove_coins_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.sender = request.user
            transaction.amount = -transaction.amount  # Отрицательное значение для удаления
            transaction.save()
            return redirect('balance')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'coins/remove_coins.html', {'form': form})

@login_required
def profile_view(request):
    if request.user.groups.filter(name='AddModerators').exists():
        return redirect('add_coins')
    elif request.user.groups.filter(name='RemoveModerators').exists():
        return redirect('remove_coins')
    else:
        balance = request.user.doscointbalance.balance
        total_earned = request.user.doscointbalance.total_earned
        return render(request, 'accounts/profile.html', {'balance': balance, 'total_earned': total_earned})
