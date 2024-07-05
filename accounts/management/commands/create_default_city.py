from django.core.management.base import BaseCommand
from accounts.models import City

class Command(BaseCommand):
    help = 'Create default cities'

    def handle(self, *args, **kwargs):
        City.create_default_city()
        self.stdout.write(self.style.SUCCESS('Successfully created or updated default cities'))
