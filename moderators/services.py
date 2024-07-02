from django.contrib.auth.models import Group, User

def add_user_to_group(user: User, group_name: str) -> bool:
    try:
        group = Group.objects.get(name=group_name)
        group.user_set.add(user)
        return True
    except Group.DoesNotExist:
        return False

def remove_user_from_group(user: User, group_name: str) -> bool:
    try:
        group = Group.objects.get(name=group_name)
        group.user_set.remove(user)
        return True
    except Group.DoesNotExist:
        return False

def list_users_in_group(group_name: str):
    try:
        group = Group.objects.get(name=group_name)
        return group.user_set.all()
    except Group.DoesNotExist:
        return []
