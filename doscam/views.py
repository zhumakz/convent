from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Event, Location
from .forms import EventForm
from accounts.models import User
from coins.models import Transaction
from friends.models import FriendRequest, Friendship

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']
            duration_minutes = form.cleaned_data['duration_minutes']
            min_friends = form.cleaned_data.get('min_friends')
            has_profile_picture = form.cleaned_data.get('has_profile_picture')

            filters = {
                'min_friends': min_friends,
                'has_profile_picture': has_profile_picture
            }
            participant1, participant2 = Event.get_random_participants(filters)

            if not participant1 or not participant2:
                messages.error(request, "Not enough participants meet the criteria.")
                return redirect('create_event')

            event = Event.objects.create(
                participant1=participant1,
                participant2=participant2,
                location=location,
                duration_minutes=duration_minutes
            )
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'doscam/create_event.html', {'form': form})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'doscam/event_detail.html', {'event': event})

@login_required
def operator_view(request):
    event = Event.objects.filter(is_completed=False).order_by('-start_time').first()
    return render(request, 'doscam/operator_view.html', {'event': event})

@login_required
def confirm_participation(request, user_id):
    user = get_object_or_404(User, id=user_id)
    event = Event.objects.filter(
        Q(participant1=user) | Q(participant2=user),
        is_completed=False
    ).first()

    if not event:
        messages.error(request, "No ongoing event for this user.")
        return redirect('operator_view')

    if event.participant1 == user:
        event.participant1_confirmed = True
    elif event.participant2 == user:
        event.participant2_confirmed = True

    event.save()  # Save the confirmation status

    if event.participant1_confirmed and event.participant2_confirmed:
        event.complete_event()
        messages.success(request, "Event completed successfully!")
    else:
        messages.info(request, "Waiting for the other participant to confirm.")

    return redirect('operator_view')