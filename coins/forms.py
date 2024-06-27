from django import forms
from .models import Transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['recipient', 'amount', 'description']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['recipient'].queryset = User.objects.exclude(id=self.user.id)

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive")

        if self.user.groups.filter(name='AddModerators').exists() and amount > 10:
            raise forms.ValidationError("AddModerators cannot send more than 10 coins per transaction")

        if self.user.groups.filter(name='RemoveModerators').exists() and self.cleaned_data['recipient'].doscointbalance.balance - amount < 0:
            raise forms.ValidationError("RemoveModerators cannot reduce balance below 0")

        if self.user.doscointbalance.balance < amount and not self.user.groups.filter(name='AddModerators').exists():
            raise forms.ValidationError("Insufficient balance")

        return cleaned_data
