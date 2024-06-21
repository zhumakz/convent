from django.conf import settings

class BaseTemplateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if request.user.is_authenticated:
            if request.user.groups.filter(name__in=['AddModerators', 'RemoveModerators']).exists():
                response.context_data['base_template'] = 'base_moderator.html'
            else:
                response.context_data['base_template'] = 'base_user.html'
        else:
            response.context_data['base_template'] = 'base_user.html'  # Или другой шаблон для неавторизованных пользователей
        return response
