from datetime import datetime, time, timedelta

from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login

from .models import Room, Reservation
from .forms import (
    ReservationForm, RegistrationForm,
    RoomForm, ReservationAdminForm, UserForm
)


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False)
            u.set_password(form.cleaned_data['password'])
            u.save()
            login(request, u)
            return redirect('reservations:room_status')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'reservations/room_list.html', {'rooms': rooms})


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
        dt = datetime.combine(chosen_date, time(hour))
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
        'min_date': min_date.isoformat(),
        'grid': grid,
    })


@login_required
def confirm_reservation(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    start_iso = request.GET.get('start_time', '').replace(' ', '+')
    end_iso = request.GET.get('end_time', '').replace(' ', '+')
    if not start_iso or not end_iso:
        return redirect('reservations:room_status')

    start_dt = datetime.fromisoformat(start_iso).replace(tzinfo=None)
    start_dt = timezone.make_aware(start_dt)
    end_dt = datetime.fromisoformat(end_iso).replace(tzinfo=None)
    end_dt = timezone.make_aware(end_dt)

    return render(request, 'reservations/confirm_reservation.html', {
        'room': room,
        'start': start_dt,
        'end': end_dt
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
            messages.success(request, "Successfully booked")
            return redirect('reservations:my_reservations')

    return render(request, 'reservations/reservation_form.html', {
        'form': form,
        'room': room
    })


@login_required
def my_reservations(request):
    upcoming = Reservation.objects.filter(
        user=request.user
    ).order_by('start_time')
    return render(request, 'reservations/my_reservations.html', {
        'reservations': upcoming
    })


@login_required
def reservation_detail(request, res_id):
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)
    return render(request, 'reservations/reservation_detail.html', {
        'res': res
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


@login_required
def edit_reservation(request, res_id):
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)
    room = res.room

    if 'date' in request.GET:
        try:
            chosen_date = datetime.fromisoformat(request.GET['date']).date()
        except ValueError:
            chosen_date = timezone.localdate()
    else:
        chosen_date = timezone.localdate()

    min_date = timezone.localdate()

    slots = []
    for hour in range(9, 17):
        dt = datetime.combine(chosen_date, time(hour))
        start = timezone.make_aware(dt)
        end = start + timedelta(hours=1)
        if start == res.start_time and end == res.end_time:
            slots.append({'start': start, 'end': end})
        else:
            if not Reservation.objects.filter(
                room=room,
                start_time__lt=end,
                end_time__gt=start
            ).exists():
                slots.append({'start': start, 'end': end})

    class SlotForm(forms.Form):
        time_slot = forms.ChoiceField(
            choices=[
                (f"{s['start'].isoformat()}|{s['end'].isoformat()}",
                 f"{s['start'].strftime('%H:%M')}–{s['end'].strftime('%H:%M')}")
                for s in slots
            ] or [('', 'No slots available')]
        )

    if request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            val = form.cleaned_data['time_slot']
            if val:
                start_iso, end_iso = val.split('|')
                new_start = timezone.make_aware(
                    datetime.fromisoformat(start_iso).replace(tzinfo=None)
                )
                new_end = timezone.make_aware(
                    datetime.fromisoformat(end_iso).replace(tzinfo=None)
                )

                conflict = Reservation.objects.filter(
                    room=room,
                    start_time__lt=new_end,
                    end_time__gt=new_start
                ).exclude(pk=res.pk).exists()

                if conflict:
                    messages.error(request, "That slot was just booked.")
                else:
                    res.start_time = new_start
                    res.end_time = new_end
                    res.save()
                    messages.success(request, "Reservation updated")
                    return redirect('reservations:my_reservations')
            else:
                messages.error(request, "No slot selected")
    else:
        form = SlotForm()

    return render(request, 'reservations/edit_reservation.html', {
        'room': room,
        'res': res,
        'form': form,
        'chosen_date': chosen_date,
        'min_date': min_date.isoformat(),
    })


# -- admin views below --

@staff_member_required
def admin_room_list(request):
    rooms = Room.objects.all()
    return render(request, 'reservations/admin_room_list.html', {'rooms': rooms})

@staff_member_required
def admin_room_edit(request, pk=None):
    inst = Room.objects.get(pk=pk) if pk else None
    form = RoomForm(request.POST or None, instance=inst)
    if form.is_valid():
        form.save()
        return redirect('reservations:admin_room_list')
    return render(request, 'reservations/admin_room_form.html', {'form': form})

@staff_member_required
def admin_room_delete(request, pk):
    obj = get_object_or_404(Room, pk=pk)
    if request.method=='POST':
        obj.delete()
        return redirect('reservations:admin_room_list')
    return render(request,'reservations/admin_confirm_delete.html',{'obj':obj})

@staff_member_required
def admin_reservation_list(request):
    rs = Reservation.objects.all().order_by('start_time')
    return render(request,'reservations/admin_reservation_list.html',{'reservations':rs})

@staff_member_required
def admin_reservation_edit(request, pk=None):
    inst = Reservation.objects.get(pk=pk) if pk else None
    form = ReservationAdminForm(request.POST or None, instance=inst)
    if form.is_valid():
        form.save()
        return redirect('reservations:admin_reservation_list')
    return render(request,'reservations/admin_reservation_form.html',{'form':form})

@staff_member_required
def admin_reservation_delete(request, pk):
    obj = get_object_or_404(Reservation, pk=pk)
    if request.method=='POST':
        obj.delete()
        return redirect('reservations:admin_reservation_list')
    return render(request,'reservations/admin_confirm_delete.html',{'obj':obj})

@staff_member_required
def admin_user_list(request):
    us = User.objects.all()
    return render(request,'reservations/admin_user_list.html',{'users':us})

@staff_member_required
def admin_user_edit(request, pk=None):
    inst = User.objects.get(pk=pk) if pk else None
    form = UserForm(request.POST or None, instance=inst)
    if form.is_valid():
        u = form.save(commit=False)
        if form.cleaned_data['password']:
            u.set_password(form.cleaned_data['password'])
        u.save()
        return redirect('reservations:admin_user_list')
    return render(request,'reservations/admin_user_form.html',{'form':form})

@staff_member_required
def admin_user_delete(request, pk):
    obj = get_object_or_404(User, pk=pk)
    if request.method=='POST':
        obj.delete()
        return redirect('reservations:admin_user_list')
    return render(request,'reservations/admin_confirm_delete.html',{'obj':obj})
