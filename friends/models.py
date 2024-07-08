from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext as __

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE, verbose_name=_("От пользователя"))
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE, verbose_name=_("К пользователю"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))

    def accept(self):
        Friendship.objects.create(user1=self.from_user, user2=self.to_user)
        self.delete()

    def __str__(self):
        return _("Запрос в друзья от {from_user} к {to_user}").format(from_user=self.from_user, to_user=self.to_user)

    class Meta:
        verbose_name = _("Запрос в друзья")
        verbose_name_plural = _("Запросы в друзья")


class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships1', on_delete=models.CASCADE, verbose_name=_("Пользователь 1"))
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships2', on_delete=models.CASCADE, verbose_name=_("Пользователь 2"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))

    def __str__(self):
        return _("{user1} дружит с {user2}").format(user1=self.user1, user2=self.user2)

    class Meta:
        verbose_name = _("Дружба")
        verbose_name_plural = _("Дружбы")
