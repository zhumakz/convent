from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def accept(self):
        Friendship.objects.create(user1=self.from_user, user2=self.to_user)
        self.delete()

    def __str__(self):
        return _("Friend request from {from_user} to {to_user}").format(from_user=self.from_user, to_user=self.to_user)


class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return _("{user1} is friends with {user2}").format(user1=self.user1, user2=self.user2)
