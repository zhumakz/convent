from django.core.management.base import BaseCommand
from points.models import PointOfInterest


class Command(BaseCommand):
    help = 'Create default points'

    def handle(self, *args, **kwargs):
        PointOfInterest.create_default_points()
        self.stdout.write(self.style.SUCCESS('Successfully created default points'))
