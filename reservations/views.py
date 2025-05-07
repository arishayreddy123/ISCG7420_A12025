from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from .models import Room, Reservation
from .forms import ReservationForm

@login_required
def room_status(request):
    rooms = Room.objects.all()
    return render(request, 'reservations/room_status.html', {'rooms': rooms})

@login_required
def make_reservation(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            res = form.save(commit=False)
            res.user = request.user
            res.room = room
            # conflict check
            if Reservation.objects.filter(
                    room=room,
                    start_time__lt=res.end_time,
                    end_time__gt=res.start_time
               ).exists():
                form.add_error(None, "Time slot conflict.")
            else:
                res.save()
                # send confirmation email
                send_mail(
                  'Booking Confirmed',
                  f'Your booking of {room.name} at {res.start_time} is confirmed.',
                  'noreply@unitec.ac.nz',
                  [request.user.email],
                )
                return redirect('reservations:my_reservations')
    else:
        form = ReservationForm(initial={
            'start_time': timezone.now(),
            'end_time': timezone.now()
        })
    return render(request, 'reservations/reservation_form.html', {'form': form, 'room': room})

@login_required
def my_reservations(request):
    upcoming = Reservation.objects.filter(
        user=request.user,
        end_time__gte=timezone.now()
    ).order_by('start_time')
    return render(request, 'reservations/my_reservations.html', {'reservations': upcoming})

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
    return render(request, 'reservations/reservation_form.html', {'form': form, 'room': res.room})

@login_required
def cancel_reservation(request, res_id):
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)
    if request.method == 'POST':
        res.delete()
        return redirect('reservations:my_reservations')
    return render(request, 'reservations/confirm_cancel.html', {'reservation': res})
