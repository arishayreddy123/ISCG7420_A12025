from datetime import datetime, time, timedelta
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import login
from .models import Room, Reservation
from .forms import ReservationForm, RegistrationForm

@login_required
def room_status(request):
    min_date = timezone.localdate()
    date_str = request.GET.get('date', min_date.isoformat())
    try:
        chosen_date = datetime.fromisoformat(date_str).date()
    except ValueError:
        chosen_date = min_date

    slots = []
    for hour in range(9, 17):
        dt = datetime.combine(chosen_date, time(hour, 0))
        start = timezone.make_aware(dt)
        end = start + timedelta(hours=1)
        slots.append({'start': start, 'end': end})

    rooms = Room.objects.all()
    todays = Reservation.objects.filter(start_time__date=chosen_date)

    grid = []
    for room in rooms:
        row = {'room': room, 'cells': []}
        for slot in slots:
            conflict = todays.filter(
                room=room,
                start_time__lt=slot['end'],
                end_time__gt=slot['start']
            ).exists()
            row['cells'].append({
                'start': slot['start'],
                'end': slot['end'],
                'free': not conflict
            })
        grid.append(row)

    return render(request, 'reservations/room_grid.html', {
        'date': chosen_date,
        'date_str': chosen_date.isoformat(),
        'min_date': min_date.isoformat(),
        'slots': slots,
        'grid': grid,
    })

@login_required
def confirm_reservation(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    start_iso = request.GET.get('start_time')
    end_iso   = request.GET.get('end_time')
    if not start_iso or not end_iso:
        return redirect('reservations:room_status')

    # parse ISO; fromisoformat on offset gives aware, so only make_aware if naive
    start_dt = datetime.fromisoformat(start_iso)
    if start_dt.tzinfo is None:
        start_dt = timezone.make_aware(start_dt)
    end_dt = datetime.fromisoformat(end_iso)
    if end_dt.tzinfo is None:
        end_dt = timezone.make_aware(end_dt)

    return render(request, 'reservations/confirm_reservation.html', {
        'room': room,
        'start': start_dt,
        'end': end_dt,
    })

@login_required
def make_reservation(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method != 'POST':
        return redirect('reservations:room_status')

    form = ReservationForm(request.POST)
    if form.is_valid():
        res = form.save(commit=False)
        res.user = request.user
        res.room = room
        if Reservation.objects.filter(
            room=room,
            start_time__lt=res.end_time,
            end_time__gt=res.start_time
        ).exists():
            form.add_error(None, "Time slot conflict.")
        else:
            res.save()
            send_mail(
              'Booking Confirmed',
              f'Your booking of {room.name} at {res.start_time} is confirmed.',
              'noreply@unitec.ac.nz',
              [request.user.email],
            )
            messages.success(request, "Successfully booked")
            return redirect('reservations:my_reservations')

    return render(request, 'reservations/reservation_form.html', {
        'form': form,
        'room': room
    })

@login_required
def my_reservations(request):
    today = timezone.localdate()
    upcoming = Reservation.objects.filter(
        user=request.user,
        start_time__date__gte=today
    ).order_by('start_time')
    return render(request, 'reservations/my_reservations.html', {
        'reservations': upcoming
    })

@login_required
def edit_reservation(request, res_id):
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)
    room = res.room

    min_date = timezone.localdate()
    date_str = request.GET.get('date', res.start_time.date().isoformat())
    try:
        chosen_date = datetime.fromisoformat(date_str).date()
    except ValueError:
        chosen_date = res.start_time.date()

    slots = []
    for hour in range(9, 17):
        dt = datetime.combine(chosen_date, time(hour, 0))
        start = timezone.make_aware(dt)
        end = start + timedelta(hours=1)
        if not (start == res.start_time and end == res.end_time):
            conflict = Reservation.objects.filter(
                room=room,
                start_time__lt=end,
                end_time__gt=start
            ).exists()
            if not conflict:
                slots.append({'start': start, 'end': end})

    class EditForm(forms.Form):
        date      = forms.DateField(
                        initial=chosen_date,
                        widget=forms.DateInput(attrs={'type':'date','min':min_date.isoformat()})
                    )
        time_slot = forms.ChoiceField(
                        choices=[(
                            f"{s['start'].isoformat()}|{s['end'].isoformat()}",
                            f"{s['start'].strftime('%H:%M')}–{s['end'].strftime('%H:%M')}"
                          ) for s in slots] or [('', 'No slots available')]
                    )

    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            val = form.cleaned_data['time_slot']
            if val:
                start_iso, end_iso = val.split('|')
                new_start = datetime.fromisoformat(start_iso)
                new_end   = datetime.fromisoformat(end_iso)
                res.start_time = new_start if new_start.tzinfo else timezone.make_aware(new_start)
                res.end_time   = new_end   if new_end.tzinfo   else timezone.make_aware(new_end)
                res.save()
                messages.success(request, "Reservation updated")
            else:
                messages.error(request, "No slot selected")
            return redirect('reservations:my_reservations')
    else:
        form = EditForm()

    return render(request, 'reservations/edit_reservation.html', {
        'room': room,
        'res': res,
        'form': form,
    })

@login_required
def cancel_reservation(request, res_id):
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)
    if request.method == 'POST':
        res.delete()
        messages.success(request, "Reservation cancelled")
        return redirect('reservations:my_reservations')
    return render(request, 'reservations/confirm_cancel.html', {
        'reservation': res
    })

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('reservations:room_status')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
