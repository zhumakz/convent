from django import forms

class SendCoinsForm(forms.Form):
    user_id = forms.IntegerField(label='User ID')
    amount = forms.DecimalField(label='Amount', max_digits=10, decimal_places=2)
    description = forms.CharField(label='Description', max_length=255, required=False)
