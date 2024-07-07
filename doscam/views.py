from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _, gettext as __
from django.http import JsonResponse
from django.utils import timezone
from .forms import EventForm
from .services import EventService
from accounts.models import User
from .models import Event, Location
import logging

logger = logging.getLogger(__name__)


@login_required
def create_event(request):
    participants = {}
    location = None
    error_message = None
    ready_participants_count = EventService.get_ready_participants_count()

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            # Проверка на наличие активного события
            if EventService.check_active_event():
                error_message = _("An active event is already in progress. Please wait until it is completed.")
            else:
                try:
                    duration_minutes = form.cleaned_data['duration_minutes']
                    has_profile_picture = form.cleaned_data.get('has_profile_picture')

                    participant1_id = request.POST.get('participant1_id')
                    participant2_id = request.POST.get('participant2_id')
                    location_id = request.POST.get('location_id')

                    participant1 = User.objects.get(id=participant1_id)
                    participant2 = User.objects.get(id=participant2_id)
                    location = Location.objects.get(id=location_id)

                    event, error_message = EventService.create_event_with_params(
                        participant1, participant2, location, duration_minutes, has_profile_picture,
                        request.POST.get('publish') == 'true'
                    )

                    if not error_message:
                        return redirect('operator_view')
                except User.DoesNotExist:
                    error_message = _("One of the participants does not exist.")
                except Location.DoesNotExist:
                    error_message = _("The selected location does not exist.")
                except Exception as e:
                    logger.error(str(e))
                    error_message = _("An unexpected error occurred.")
    else:
        form = EventForm()
        participant1, participant2, location = EventService.get_random_participants_and_location()
        if participant1 and participant2 and location:
            participants['participant1'] = participant1
            participants['participant2'] = participant2

    return render(request, 'doscam/create_event.html', {
        'form': form,
        'participants': participants,
        'location': location,
        'ready_participants_count': ready_participants_count,
        'error_message': error_message
    })


@login_required
def operator_view(request):
    active_event = EventService.check_active_event()
    return render(request, 'doscam/operator_view.html', {
        'event': active_event,
        'server_time': timezone.now().isoformat() if active_event else None
    })


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participants = {
        'participant1': event.participant1,
        'participant2': event.participant2
    }
    return render(request, 'doscam/event_detail.html', {'event': event, 'participants': participants})


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
    try:
        participant1, participant2, location = EventService.get_random_participants_and_location()
        if not participant1 or not participant2 or not location:
            return JsonResponse({'error': "Not enough participants or no location available."}, status=400)

        return JsonResponse({
            'participant1_id': participant1.id,
            'participant1_name': participant1.name,
            'participant1_surname': participant1.surname,
            'participant1_city': participant1.city,
            'participant1_profile_photo': participant1.profile_picture.url,
            'participant2_id': participant2.id,
            'participant2_name': participant2.name,
            'participant2_surname': participant2.surname,
            'participant2_city': participant2.city,
            'participant2_profile_photo': participant2.profile_picture.url,
            'location_id': location.id,
            'location_name': location.name
        })
    except Exception as e:
        logger.error(str(e))
        return JsonResponse({'error': "An unexpected error occurred."}, status=500)


@login_required
def publish_event(request, event_id):
    try:
        event = get_object_or_404(Event, id=event_id)
        if event.is_draft:
            event.is_published = True
            event.is_draft = False
            event.save()
            return JsonResponse({'message': "Event published successfully!"})
        else:
            return JsonResponse({'error': "Event is already published."}, status=400)
    except Exception as e:
        logger.error(str(e))
        return JsonResponse({'error': "An unexpected error occurred."}, status=500)


@login_required
def stop_event(request, event_id):
    try:
        event = get_object_or_404(Event, id=event_id)
        event.is_completed = True
        event.is_published = False
        event.save()
        messages.success(request, _("Event has been stopped successfully."))
    except Exception as e:
        logger.error(str(e))
        messages.error(request, _("An unexpected error occurred while stopping the event."))
    return redirect('operator_view')


@login_required
def find_view(request):
    user = request.user
    # Проверка текущего события

    current_event = EventService.check_active_event_by_user(user)

    return render(request, 'doscam/find.html', {
        'user': user,
        'current_event': current_event,
        'is_event_participant': current_event and (
                current_event.participant1 == user or current_event.participant2 == user)
    })
