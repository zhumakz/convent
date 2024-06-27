from django.shortcuts import render, get_object_or_404
from .models import StaticPage

def static_page_list(request):
    pages = StaticPage.objects.all()
    return render(request, 'static_pages/static_page_list.html', {'pages': pages})

def static_page_detail(request, page_id):
    page = get_object_or_404(StaticPage, id=page_id)
    return render(request, 'static_pages/static_page_detail.html', {'page': page})
