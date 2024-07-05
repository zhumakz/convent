from django.core.management.base import BaseCommand
from campaigns.models import Campaign


class Command(BaseCommand):
    help = 'Create default campaigns'

    def handle(self, *args, **kwargs):
        Campaign.create_default_campaigns()
        self.stdout.write(self.style.SUCCESS('Successfully created default campaigns'))
