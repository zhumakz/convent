from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import DoscointBalance

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        DoscointBalance.objects.get_or_create(user=instance)
