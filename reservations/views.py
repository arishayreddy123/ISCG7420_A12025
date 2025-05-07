from datetime import datetime, time, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
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

    # parse ISO strings into datetimes and make them timezone-aware
    start_dt = timezone.make_aware(datetime.fromisoformat(start_iso))
    end_dt   = timezone.make_aware(datetime.fromisoformat(end_iso))

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
            return redirect('reservations:my_reservations')

    return render(request, 'reservations/reservation_form.html', {
        'form': form,
        'room': room
    })

@login_required
def my_reservations(request):
    upcoming = Reservation.objects.filter(
        user=request.user,
        end_time__gte=timezone.now()
    ).order_by('start_time')
    return render(request, 'reservations/my_reservations.html', {
        'reservations': upcoming
    })

@login_required
def edit_reservation(request, res_id):
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=res)
        if form.is_valid():
            form.save()
            return redirect('reservations:my_reservations')
    else:
        form = ReservationForm(instance=res)
    return render(request, 'reservations/reservation_form.html', {
        'form': form,
        'room': res.room
    })

@login_required
def cancel_reservation(request, res_id):
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)
    if request.method == 'POST':
        res.delete()
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
