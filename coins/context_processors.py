from .models import DoscointBalance

def add_balance_to_context(request):
    if request.user.is_authenticated:
        try:
            balance = DoscointBalance.objects.get(user=request.user).balance
            return {'user_balance': balance}
        except DoscointBalance.DoesNotExist:
            return {'user_balance': 0}
    return {}
