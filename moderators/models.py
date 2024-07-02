from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_moderator_groups(sender, **kwargs):
    if sender.name == 'moderators':
        groups = {
            'Главный оператор': [],
            'Оператор': [],
            'Продавец': [],
            'Оператор Doscam': []
        }

        for group_name, permissions in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                for perm in permissions:
                    permission = Permission.objects.get(codename=perm)
                    group.permissions.add(permission)
                print(f'Created group: {group_name} with permissions: {permissions}')

        # Remove the old groups if they exist
        old_groups = ['AddCoinsModerators', 'RemoveCoinsModerators']
        for old_group in old_groups:
            try:
                Group.objects.get(name=old_group).delete()
                print(f'Removed old group: {old_group}')
            except Group.DoesNotExist:
                pass
