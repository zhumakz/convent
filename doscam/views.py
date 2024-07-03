from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _, gettext as __
from django.http import JsonResponse
from .forms import EventForm
from .services import EventService
from accounts.models import User
from .models import Event
import logging

logger = logging.getLogger(__name__)

@login_required
def create_event(request):
    participants = {}
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']
            duration_minutes = form.cleaned_data['duration_minutes']
            min_friends = form.cleaned_data.get('min_friends')
            has_profile_picture = form.cleaned_data.get('has_profile_picture')

            event, error_message = EventService.create_event(location, duration_minutes, min_friends, has_profile_picture, request.POST.get('publish') == 'true')

            if error_message:
                messages.error(request, error_message)
                return redirect('create_event')

            return redirect('operator_view')
    else:
        form = EventForm()
        participant1, participant2 = Event.get_random_participants({})
        if participant1 and participant2:
            participants['participant1'] = participant1
            participants['participant2'] = participant2

    return render(request, 'doscam/create_event.html', {'form': form, 'participants': participants})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'doscam/event_detail.html', {'event': event})

@login_required
def operator_view(request):
    event = Event.objects.filter(is_published=True, is_completed=False).order_by('-start_time').first()
    return render(request, 'doscam/operator_view.html', {'event': event})

@login_required
def confirm_participation(request, user_id):
    user = get_object_or_404(User, id=user_id)
    event = Event.objects.filter(
        Q(participant1=user) | Q(participant2=user),
        is_completed=False,
        is_published=True
    ).select_related('participant1', 'participant2').first()

    if not event:
        messages.error(request, __("No ongoing event for this user."))
        return redirect('operator_view')

    success, message = EventService.confirm_participation(user, event)
    if success:
        messages.success(request, message)
    else:
        messages.info(request, message)

    return redirect('operator_view')

@login_required
def randomize_participants(request):
    participant1, participant2 = Event.get_random_participants({})

    if not participant1 or not participant2:
        return JsonResponse({'error': "Not enough participants meet the criteria."}, status=400)

    return JsonResponse({'participant1': participant1.username, 'participant2': participant2.username})

@login_required
def publish_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.is_draft:
        event.is_published = True
        event.is_draft = False
        event.save()
        return JsonResponse({'message': "Event published successfully!"})
    else:
        return JsonResponse({'error': "Event is already published."}, status=400)
