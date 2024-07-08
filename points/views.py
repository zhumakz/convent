from django.shortcuts import render, redirect
from .models import PointOfInterest

def point_list(request):
    points = PointOfInterest.objects.all().order_by('id')
    return render(request, 'points/point_list.html', {'points': points})