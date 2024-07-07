from django.core.management.base import BaseCommand
from doscam.models import Location

class Command(BaseCommand):
    help = 'Add default locations to the database'

    def handle(self, *args, **kwargs):
        Location.create_default_locations()
        self.stdout.write(self.style.SUCCESS("Successfully added default locations"))
