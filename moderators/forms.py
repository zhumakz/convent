from django import forms


class SendCoinsForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    amount = forms.DecimalField(label='Amount', max_digits=10, decimal_places=2)
