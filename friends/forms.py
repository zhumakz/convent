from django import forms
from .models import FriendRequest, Friendship
from accounts.models import User

class FriendRequestForm(forms.ModelForm):
    class Meta:
        model = FriendRequest
        fields = ['to_user']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(FriendRequestForm, self).__init__(*args, **kwargs)
        self.fields['to_user'].queryset = User.objects.exclude(id=self.user.id)

    def clean_to_user(self):
        to_user = self.cleaned_data.get('to_user')
        if to_user == self.user:
            raise forms.ValidationError("Вы не можете добавить себя в друзья.")
        if FriendRequest.objects.filter(from_user=self.user, to_user=to_user).exists():
            raise forms.ValidationError("Вы уже отправили запрос этому пользователю.")
        if Friendship.objects.filter(user1=self.user, user2=to_user).exists() or Friendship.objects.filter(user1=to_user, user2=self.user).exists():
            raise forms.ValidationError("Этот пользователь уже ваш друг.")
        return to_user

class ConfirmFriendRequestForm(forms.ModelForm):
    class Meta:
        model = FriendRequest
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        from_user = self.instance.from_user
        to_user = self.instance.to_user
        if Friendship.objects.filter(user1=from_user, user2=to_user).exists() or Friendship.objects.filter(user1=to_user, user2=from_user).exists():
            raise forms.ValidationError("Этот пользователь уже ваш друг.")
        return cleaned_data
