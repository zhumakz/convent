import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from coins.models import Transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create groups and permissions for user roles'

    def handle(self, *args, **kwargs):
        # Permissions
        content_type = ContentType.objects.get_for_model(Transaction)
        can_add_coins, _ = Permission.objects.get_or_create(codename='can_add_coins', name='Can add coins', content_type=content_type)
        can_remove_coins, _ = Permission.objects.get_or_create(codename='can_remove_coins', name='Can remove coins', content_type=content_type)

        # Groups
        user_group, created = Group.objects.get_or_create(name='Users')
        if created:
            logger.info('Created Users group')

        add_moderator_group, created = Group.objects.get_or_create(name='AddModerators')
        if created:
            add_moderator_group.permissions.add(can_add_coins)
            logger.info('Created AddModerators group and assigned permissions')

        remove_moderator_group, created = Group.objects.get_or_create(name='RemoveModerators')
        if created:
            remove_moderator_group.permissions.add(can_remove_coins)
            logger.info('Created RemoveModerators group and assigned permissions')

        admin_group, created = Group.objects.get_or_create(name='Admins')
        if created:
            admin_group.permissions.set(Permission.objects.all())
            logger.info('Created Admins group and assigned all permissions')

        self.stdout.write(self.style.SUCCESS('Successfully created user roles and permissions'))
