from django.shortcuts import render, get_object_or_404
from .models import StaticPage


def static_page_list(request):
    pages = StaticPage.objects.all()
    return render(request, 'static_pages/static_page_list.html', {'pages': pages})


def static_page_detail(request, page_id):
    page = get_object_or_404(StaticPage, id=page_id)
    return render(request, 'static_pages/static_page_detail.html', {'page': page})


def about_coins_view(request):
    about_coins_page = get_object_or_404(StaticPage, title='about-coins')
    return render(request, 'static_pages/about_coins.html', {'page': about_coins_page})


def map_view(request):
    map_page = get_object_or_404(StaticPage, title='map')
    return render(request, 'static_pages/map.html', {'page': map_page})
