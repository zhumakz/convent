from django.conf import settings

def base_template(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name__in=['AddModerators', 'RemoveModerators']).exists():
            return {'base_template': 'base_moderator.html'}
        else:
            return {'base_template': 'base_user.html'}
    else:
        return {'base_template': 'base_user.html'}  # Или другой шаблон для неавторизованных пользователей
