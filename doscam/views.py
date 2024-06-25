from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django import forms
from .models import Event
from accounts.models import User


@login_required
def operator_view(request):
    event = Event.objects.filter(
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now(),
        is_completed=False
    ).first()

    return render(request, 'doscam/operator_view.html', {'event': event})


@login_required
def scan_qr_code_view(request, qr_data):
    try:
        user_id = int(qr_data)
        user = get_object_or_404(User, id=user_id)
        event = Event.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now(),
            is_completed=False,
            participant1=user
        ).first() or Event.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now(),
            is_completed=False,
            participant2=user
        ).first()

        if event:
            event.complete_event()
            return render(request, 'doscam/event_completed.html', {'event': event})
        else:
            return render(request, 'doscam/no_active_event.html')

    except (ValueError, User.DoesNotExist):
        return render(request, 'doscam/invalid_qr.html')


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['start_time', 'end_time', 'location']


@login_required
def create_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            participants = User.objects.filter(is_active=True).order_by('?')[:2]
            if len(participants) >= 2:
                event.participant1 = participants[0]
                event.participant2 = participants[1]
                event.save()
                return redirect('operator_view')
    else:
        form = EventForm()
    return render(request, 'doscam/create_event.html', {'form': form})

@login_required
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'doscam/event_detail.html', {'event': event})