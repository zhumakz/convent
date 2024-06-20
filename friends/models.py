from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from coins.models import DoscointBalance, Transaction
from accounts.models import User  # Убедитесь, что импортировали модель User

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Friend request from {self.from_user} to {self.to_user}"

class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1} is friends with {self.user2}"

@receiver(post_save, sender=Friendship)
def add_coins_on_friendship(sender, instance, created, **kwargs):
    if created:
        user1 = instance.user1
        user2 = instance.user2
        if user1.city == user2.city:
            coins = settings.COINS_SAME_CITY
        else:
            coins = settings.COINS_DIFFERENT_CITY

        # Обновляем баланс пользователей
        user1.doscointbalance.balance += coins
        user2.doscointbalance.balance += coins
        user1.doscointbalance.save()
        user2.doscointbalance.save()

        # Создаем транзакции
        Transaction.objects.create(sender=user1, recipient=user1, amount=coins, description='Friendship bonus')
        Transaction.objects.create(sender=user2, recipient=user2, amount=coins, description='Friendship bonus')
