from django.shortcuts import redirect
from django.urls import reverse


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.get('language') and not request.path.startswith(reverse('select_language')):
            return redirect('select_language')
        response = self.get_response(request)
        return response
