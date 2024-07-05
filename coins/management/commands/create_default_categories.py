from django.core.management.base import BaseCommand
from coins.models import TransactionCategory

class Command(BaseCommand):
    help = 'Create default transaction categories'

    def handle(self, *args, **kwargs):
        TransactionCategory.create_default_categories()
        self.stdout.write(self.style.SUCCESS('Successfully created default transaction categories'))
