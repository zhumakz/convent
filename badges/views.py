# badges/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Badge
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_badge(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    badge, created = Badge.objects.get_or_create(user=user)
    if created or 'regenerate' in request.GET:
        badge.create_badge()
    return render(request, 'badges/badge.html', {'badge': badge})
