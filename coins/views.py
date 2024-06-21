from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DoscointBalance, Transaction
from .forms import TransactionForm
from .decorators import add_coins_permission_required, remove_coins_permission_required


@login_required
def balance_view(request):
    balance = request.user.doscointbalance.balance
    transactions = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(recipient=request.user)
    transactions = transactions.order_by('-timestamp')

    for transaction in transactions:
        if transaction.is_system_transaction:
            transaction.sender_name = "System"
            transaction.recipient_name = f"{transaction.recipient.name} {transaction.recipient.surname}"
        else:
            if transaction.sender == request.user:
                transaction.sender_name = "You"
            else:
                if transaction.sender.is_superuser:
                    transaction.sender_name = "System"
                elif transaction.sender.groups.filter(name__in=['AddModerators', 'RemoveModerators']).exists():
                    transaction.sender_name = f"{transaction.sender.name} {transaction.sender.surname}"
                else:
                    transaction.sender_name = transaction.sender.phone_number

            if transaction.recipient == request.user:
                transaction.recipient_name = "You"
            else:
                transaction.recipient_name = f"{transaction.recipient.name} {transaction.recipient.surname}"

    return render(request, 'coins/balance.html', {'balance': balance, 'transactions': transactions})

@login_required
@add_coins_permission_required
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
@remove_coins_permission_required
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
