from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

from accounts.models import User
from coins.services import CoinService
from moderators.forms import SendCoinsForm


def is_moderator(user):
    return user.groups.filter(name__in=['Главный оператор', 'Оператор', 'Продавец', 'Оператор Doscam']).exists()


@login_required
@permission_required('moderators.view_moderators', raise_exception=True)
def moderator_dashboard(request):
    return render(request, 'moderators/dashboard.html')


@login_required
@permission_required('moderators.add_coins', raise_exception=True)
def operator_view(request):
    if request.method == 'POST':
        form = SendCoinsForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            try:
                recipient = User.objects.get(id=user_id)
                CoinService.create_transaction(
                    sender=request.user,
                    recipient=recipient,
                    amount=amount,
                    description=description
                )
                messages.success(request, 'Coins successfully sent.')
            except User.DoesNotExist:
                messages.error(request, 'User with given ID does not exist.')
            return redirect('operator')
    else:
        form = SendCoinsForm()

    return render(request, 'moderators/operator.html', {'form': form})
