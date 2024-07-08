from django.conf import settings

def base_template(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name__in=['AddModerators', 'RemoveModerators']).exists():
            return {'base_template': 'base_moderator.html'}
        else:
            return {'base_template': 'base.html'}
    else:
        return {'base_template': 'base.html'}  # Или другой шаблон для неавторизованных пользователей
