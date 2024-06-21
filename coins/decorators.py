from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def user_can_add_coins(user):
    return user.is_authenticated and user.groups.filter(name='AddModerators').exists()

def user_can_remove_coins(user):
    return user.is_authenticated and user.groups.filter(name='RemoveModerators').exists()

def add_coins_permission_required(view_func):
    decorated_view_func = user_passes_test(
        user_can_add_coins,
        login_url='balance'
    )(view_func)
    return decorated_view_func

def remove_coins_permission_required(view_func):
    decorated_view_func = user_passes_test(
        user_can_remove_coins,
        login_url='balance'
    )(view_func)
    return decorated_view_func
