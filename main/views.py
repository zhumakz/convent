from django.shortcuts import render, redirect
from django.utils.translation import activate


def home_view(request):
    return render(request, 'main/home.html')


def switch_language(request, lang_code):
    activate(lang_code)
    request.session['language'] = lang_code
    return redirect(request.META.get('HTTP_REFERER', '/'))


def select_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            activate(language)
            request.session['language'] = language
            return redirect('home')
    return render(request, 'main/select_language.html')
