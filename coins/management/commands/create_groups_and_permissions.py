import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from coins.models import Transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create groups and permissions for coin moderators'

    def handle(self, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(Transaction)

        add_permission, created = Permission.objects.get_or_create(
            codename='can_add_coins',
            name='Can add coins',
            content_type=content_type
        )

        remove_permission, created = Permission.objects.get_or_create(
            codename='can_remove_coins',
            name='Can remove coins',
            content_type=content_type
        )

        add_coins_group, created = Group.objects.get_or_create(name='AddCoinsModerators')
        if created:
            add_coins_group.permissions.add(add_permission)
            logger.info('Created AddCoinsModerators group and assigned permissions')
        else:
            if not add_coins_group.permissions.filter(codename='can_add_coins').exists():
                add_coins_group.permissions.add(add_permission)
                logger.info('Updated AddCoinsModerators group with permissions')

        remove_coins_group, created = Group.objects.get_or_create(name='RemoveCoinsModerators')
        if created:
            remove_coins_group.permissions.add(remove_permission)
            logger.info('Created RemoveCoinsModerators group and assigned permissions')
        else:
            if not remove_coins_group.permissions.filter(codename='can_remove_coins').exists():
                remove_coins_group.permissions.add(remove_permission)
                logger.info('Updated RemoveCoinsModerators group with permissions')

        self.stdout.write(self.style.SUCCESS('Successfully created or updated groups and permissions'))
