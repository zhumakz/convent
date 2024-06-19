from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from coins.models import DoscointBalance

class Command(BaseCommand):
    help = 'Create initial balance for existing users'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            DoscointBalance.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS('Successfully created or ensured existence of balances for all users'))
