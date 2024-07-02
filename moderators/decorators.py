from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect


def is_in_group(group_name):
    def in_group(user):
        return user.groups.filter(name=group_name).exists() or user.is_superuser

    return user_passes_test(in_group)


def moderator_required(view_func):
    decorated_view_func = is_in_group('Главный оператор')(view_func)
    decorated_view_func = is_in_group('Оператор')(decorated_view_func)
    decorated_view_func = is_in_group('Продавец')(decorated_view_func)
    decorated_view_func = is_in_group('Оператор Doscam')(decorated_view_func)
    return decorated_view_func


def superuser_or_moderator_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(
                name__in=['Главный оператор', 'Оператор', 'Продавец', 'Оператор Doscam']).exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')

    return _wrapped_view_func
