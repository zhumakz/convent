from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Attraction
from .forms import AttractionForm


def attraction_list(request):
    attractions = Attraction.objects.all()
    return render(request, 'attractions/attraction_list.html', {'attractions': attractions})


def attraction_detail(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    return render(request, 'attractions/attraction_detail.html', {'attraction': attraction})


def attraction_detail_json(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    data = {
        'title': attraction.title,
        'description': attraction.description,
        'photo': attraction.photo.url,
        'start_time': attraction.start_time.strftime('%H:%M'),
        'end_time': attraction.end_time.strftime('%H:%M'),
        'location': attraction.location
    }
    return JsonResponse(data)


@login_required
def create_attraction(request):
    if request.method == 'POST':
        form = AttractionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('attraction_list')
    else:
        form = AttractionForm()
    return render(request, 'attractions/create_attraction.html', {'form': form})


@login_required
def edit_attraction(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    if request.method == 'POST':
        form = AttractionForm(request.POST, request.FILES, instance=attraction)
        if form.is_valid():
            form.save()
            return redirect('attraction_detail', attraction_id=attraction.id)
    else:
        form = AttractionForm(instance=attraction)
    return render(request, 'attractions/edit_attraction.html', {'form': form})
