from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import DoscointBalance


@receiver(post_save, sender=User)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        DoscointBalance.objects.get_or_create(user=instance)
