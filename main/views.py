from django.shortcuts import render, redirect
from django.utils import translation
from django.utils.translation import activate
from django.urls import reverse


def home_view(request):
    return render(request, 'main/home.html')


def switch_language(request, lang_code):
    translation.activate(lang_code)
    request.session['language'] = lang_code
    return redirect(reverse('home'))


def select_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            activate(language)
            request.session['language'] = language
            return redirect(reverse('home'))
    return render(request, 'main/select_language.html')
