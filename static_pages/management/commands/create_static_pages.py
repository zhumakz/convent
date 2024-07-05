from django.core.management.base import BaseCommand
from static_pages.models import StaticPage

class Command(BaseCommand):
    help = 'Create default static pages'

    def handle(self, *args, **kwargs):
        StaticPage.create_static_pages()
        self.stdout.write(self.style.SUCCESS('Successfully created default static pages'))
