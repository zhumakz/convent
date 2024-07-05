from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Create default city, campaigns, and other default data'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.NOTICE('Creating default city...'))
            call_command('create_default_city')
            self.stdout.write(self.style.SUCCESS('Default city created successfully.'))

            self.stdout.write(self.style.NOTICE('Creating default campaigns...'))
            call_command('create_default_campaigns')
            self.stdout.write(self.style.SUCCESS('Default campaigns created successfully.'))

            self.stdout.write(self.style.NOTICE('Creating default transactions categories...'))
            call_command('create_default_categories')
            self.stdout.write(self.style.SUCCESS('Default transactions categories created successfully.'))

            self.stdout.write(self.style.NOTICE('Creating default static_pages...'))
            call_command('create_static_pages')
            self.stdout.write(self.style.SUCCESS('Default static_pages created successfully.'))

            # Добавьте дополнительные команды здесь
            # self.stdout.write(self.style.NOTICE('Creating default XYZ...'))
            # call_command('create_default_xyz')
            # self.stdout.write(self.style.SUCCESS('Default XYZ created successfully.'))

            self.stdout.write(self.style.SUCCESS('All default data created successfully.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))