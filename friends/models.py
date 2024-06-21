from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from coins.models import DoscointBalance, Transaction

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
            coins = settings.SAME_CITY_FRIEND_REWARD
        else:
            coins = settings.DIFFERENT_CITY_FRIEND_REWARD

        # Обновляем баланс пользователей и создаем транзакции
        for user, friend in [(user1, user2), (user2, user1)]:
            doscoint_balance, created = DoscointBalance.objects.get_or_create(user=user)
            doscoint_balance.balance += coins
            doscoint_balance.total_earned += coins
            doscoint_balance.save()

            # Создаем транзакции
            Transaction.objects.create(
                sender=user,
                recipient=user,
                amount=coins,
                description=f'Reward for adding friend {friend.name} {friend.surname}',
                is_system_transaction=True
            )

        # Удаляем все запросы на дружбу между этими пользователями
        FriendRequest.objects.filter(from_user=user1, to_user=user2).delete()
        FriendRequest.objects.filter(from_user=user2, to_user=user1).delete()
