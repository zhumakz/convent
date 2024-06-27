from django.shortcuts import render


def home_view(request):
    return render(request, 'main/home.html')


from django.shortcuts import redirect
from django.utils.translation import activate


def switch_language(request, lang_code):
    activate(lang_code)
    return redirect(request.META.get('HTTP_REFERER', '/'))
