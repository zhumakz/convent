from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _, gettext as __
from .forms import EventForm
from .services import EventService
from accounts.models import User
from .models import Event
import logging

logger = logging.getLogger(__name__)


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']
            duration_minutes = form.cleaned_data['duration_minutes']
            min_friends = form.cleaned_data.get('min_friends')
            has_profile_picture = form.cleaned_data.get('has_profile_picture')

            event, error_message = EventService.create_event(location, duration_minutes, min_friends,
                                                             has_profile_picture)

            if error_message:
                messages.error(request, error_message)
                return redirect('create_event')

            return redirect('event_detail')
    else:
        form = EventForm()
    return render(request, 'doscam/create_event.html', {'form': form})


@login_required
def event_detail(request):
    event = Event.objects.filter(
        (Q(participant1=request.user) | Q(participant2=request.user)) & Q(is_completed=False)
    ).select_related('participant1', 'participant2', 'location').first()

    if not event:
        messages.error(request, __("No ongoing event found for the current user."))
        return redirect('create_event')

    return render(request, 'doscam/event_detail.html', {'event': event})


@login_required
def operator_view(request):
    event = Event.objects.filter(is_completed=False).order_by('-start_time').select_related('location').first()
    return render(request, 'doscam/operator_view.html', {'event': event})


@login_required
def confirm_participation(request, user_id):
    user = get_object_or_404(User, id=user_id)
    event = Event.objects.filter(
        Q(participant1=user) | Q(participant2=user),
        is_completed=False
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
