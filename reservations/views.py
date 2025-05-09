from datetime import datetime, date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Room, Reservation
from .forms import RegistrationForm, RoomForm, ReservationForm, UserForm

# --- PUBLIC VIEWS ---

def home(request):
    # show homepage
    return render(request, 'home.html')

def register(request):
    # handle user signup
    if request.method == 'POST':
        form = RegistrationForm(request.POST)      # use signup form
        if form.is_valid():
            user = form.save()                    # create user
            login(request, user)                  # log them in
            return redirect('reservations:home')  # go home
    else:
        form = RegistrationForm()                  # empty form
    return render(request, 'registration/register.html', {'form': form})

@login_required
def room_list(request):
    # list all rooms
    rooms = Room.objects.all()
    return render(request, 'reservations/room_list.html', {'rooms': rooms})

@login_required
def room_status(request):
    # show availability grid for chosen date
    today = date.today()
    raw = request.GET.get('date')
    sel_date = datetime.fromisoformat(raw).date() if raw else today

    min_date = today.isoformat()
    # build hourly slots
    slots = []
    for hour in range(9, 17):
        start = datetime.combine(sel_date, datetime.min.time()) + timedelta(hours=hour)
        end = start + timedelta(hours=1)
        slots.append((start, end))

    # build grid per room
    grid = []
    for room in Room.objects.all():
        cells = []
        for start, end in slots:
            booked = Reservation.objects.filter(
                room=room, start_time__lt=end, end_time__gt=start
            ).exists()
            cells.append({'free': not booked, 'start': start, 'end': end})
        grid.append({'room': room, 'cells': cells})

    return render(request, 'reservations/room_grid.html', {
        'grid': grid, 'slots': slots, 'sel_date': sel_date, 'min_date': min_date
    })

@login_required
def confirm_reservation(request, room_id):
    # show confirmation before booking
    room = get_object_or_404(Room, pk=room_id)
    try:
        start = datetime.fromisoformat(request.GET['start_time'])
        end = datetime.fromisoformat(request.GET['end_time'])
    except KeyError:
        messages.error(request, "Missing time parameters.")
        return redirect('reservations:room_status')

    # prevent double-booking
    if Reservation.objects.filter(
        room=room, start_time__lt=end, end_time__gt=start
    ).exists():
        messages.error(request, "Time slot already booked.")
        return redirect('reservations:room_status')

    return render(request, 'reservations/confirm_booking.html', {
        'room': room, 'start': start, 'end': end
    })

@login_required
def make_reservation(request, room_id):
    # create reservation
    room = get_object_or_404(Room, pk=room_id)
    try:
        start = datetime.fromisoformat(request.GET['start_time'])
        end = datetime.fromisoformat(request.GET['end_time'])
    except KeyError:
        messages.error(request, "Missing time parameters.")
        return redirect('reservations:room_status')

    # check again for conflicts
    if Reservation.objects.filter(
        room=room, start_time__lt=end, end_time__gt=start
    ).exists():
        messages.error(request, "Time slot already booked.")
        return redirect('reservations:room_status')

    Reservation.objects.create(
        room=room, user=request.user,
        start_time=start, end_time=end,
    )
    messages.success(request, "Successfully booked!")
    return redirect('reservations:my_reservations')

@login_required
def my_reservations(request):
    # list upcoming bookings for user
    today = timezone.localdate()
    upcoming = Reservation.objects.filter(
        user=request.user,
        start_time__date__gte=today
    ).order_by('start_time')
    return render(request, 'reservations/my_reservations.html', {
        'reservations': upcoming
    })

@login_required
def reservation_detail(request, res_id):
    # show one reservation
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)
    return render(request, 'reservations/reservation_detail.html', {'res': res})

@login_required
def edit_reservation(request, res_id):
    # change a booking slot
    today = date.today()
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)

    if request.method == 'POST':
        st, en = request.POST['time_slot'].split('|')
        start = datetime.fromisoformat(st)
        end = datetime.fromisoformat(en)

        conflict = Reservation.objects.filter(
            room=res.room, start_time__lt=end, end_time__gt=start
        ).exclude(pk=res.pk).exists()

        if conflict:
            messages.error(request, 'That slot is already taken.')
        else:
            res.start_time = start
            res.end_time = end
            res.save()
            messages.success(request, 'Reservation updated')
            return redirect('reservations:my_reservations')

    raw = request.GET.get('date')
    sel_date = datetime.fromisoformat(raw).date() if raw else res.start_time.date()
    if sel_date < today:
        sel_date = today

    # build slots for select
    slots = []
    for hour in range(9, 17):
        s = datetime.combine(sel_date, datetime.min.time()) + timedelta(hours=hour)
        e = s + timedelta(hours=1)
        free = not Reservation.objects.filter(
            room=res.room, start_time__lt=e, end_time__gt=s
        ).exclude(pk=res.pk).exists()
        slots.append({'start': s, 'end': e, 'free': free})

    return render(request, 'reservations/edit_reservation.html', {
        'res': res, 'slots': slots, 'sel_date': sel_date,
        'min_date': today.isoformat()
    })

@login_required
def cancel_reservation(request, res_id):
    # confirm then delete booking
    res = get_object_or_404(Reservation, pk=res_id, user=request.user)
    if request.method == 'POST':
        res.delete()
        messages.success(request, 'Reservation cancelled')
        return redirect('reservations:my_reservations')
    return render(request, 'reservations/confirm_cancel.html', {'res': res})

# --- ADMIN VIEWS ---

@staff_member_required
def admin_room_list(request):
    # list rooms for admin
    rooms = Room.objects.all()
    return render(request, 'reservations/admin_room_list.html', {'rooms': rooms})

@staff_member_required
def admin_room_add(request):
    # add new room
    form = RoomForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Room added')
        return redirect('reservations:admin_room_list')
    return render(request, 'reservations/admin_room_form.html', {
        'form': form, 'title': 'Add Room'
    })

@staff_member_required
def admin_room_edit(request, pk):
    # edit existing room
    room = get_object_or_404(Room, pk=pk)
    form = RoomForm(request.POST or None, instance=room)
    if form.is_valid():
        form.save()
        messages.success(request, 'Room updated')
        return redirect('reservations:admin_room_list')
    return render(request, 'reservations/admin_room_form.html', {
        'form': form, 'title': 'Edit Room'
    })

@staff_member_required
def admin_room_delete(request, pk):
    # delete room after confirm
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Room deleted')
        return redirect('reservations:admin_room_list')
    return render(request, 'reservations/admin_confirm_delete.html', {
        'obj': room, 'type': 'room'
    })

@staff_member_required
def admin_reservation_list(request):
    # list all reservations
    reservations = Reservation.objects.select_related('room','user').all()
    return render(request, 'reservations/admin_reservation_list.html', {
        'reservations': reservations
    })

@staff_member_required
def admin_reservation_add(request):
    # admin create reservation
    today = date.today()
    raw = request.GET.get('date')
    sel_date = date.fromisoformat(raw) if raw else today

    slots = []
    sel_room = None
    if request.GET.get('room'):
        sel_room = Room.objects.filter(pk=request.GET['room']).first()

    for hour in range(9, 17):
        s = datetime.combine(sel_date, datetime.min.time()) + timedelta(hours=hour)
        e = s + timedelta(hours=1)
        booked = Reservation.objects.filter(
            room=sel_room, start_time__lt=e, end_time__gt=s
        ).exists() if sel_room else False
        slots.append({'start': s, 'end': e, 'free': not booked})

    form = ReservationForm(request.POST or None)
    if request.method == 'POST' and 'time_slot' in request.POST:
        st, en = request.POST['time_slot'].split('|')
        room = get_object_or_404(Room, pk=request.POST['room'])
        user = get_object_or_404(User, pk=request.POST['user'])

        if Reservation.objects.filter(
            room=room, start_time__lt=en, end_time__gt=st
        ).exists():
            messages.error(request, 'That slot is already taken.')
        else:
            Reservation.objects.create(
                room=room, user=user,
                start_time=datetime.fromisoformat(st),
                end_time=datetime.fromisoformat(en),
            )
            messages.success(request, 'Reservation added')
            return redirect('reservations:admin_reservation_list')

    return render(request, 'reservations/admin_reservation_form.html', {
        'form': form,
        'title': 'Add Reservation',
        'slots': slots,
        'sel_date': sel_date,
        'min_date': today.isoformat(),
    })

@staff_member_required
def admin_reservation_edit(request, pk):
    # admin edit existing reservation
    today = date.today()
    res = get_object_or_404(Reservation, pk=pk)

    raw = request.GET.get('date')
    sel_date = date.fromisoformat(raw) if raw else res.start_time.date()
    if sel_date < today:
        sel_date = today

    slots = []
    for hour in range(9, 17):
        s = datetime.combine(sel_date, datetime.min.time()) + timedelta(hours=hour)
        e = s + timedelta(hours=1)
        free = not Reservation.objects.filter(
            room=res.room, start_time__lt=e, end_time__gt=s
        ).exclude(pk=res.pk).exists()
        slots.append({'start': s, 'end': e, 'free': free})

    form = ReservationForm(request.POST or None)
    if request.method == 'POST' and 'time_slot' in request.POST:
        st, en = request.POST['time_slot'].split('|')
        start = datetime.fromisoformat(st)
        end = datetime.fromisoformat(en)

        conflict = Reservation.objects.filter(
            room=res.room, start_time__lt=end, end_time__gt=start
        ).exclude(pk=res.pk).exists()

        if conflict:
            messages.error(request, 'That slot is already taken.')
        else:
            res.start_time = start
            res.end_time = end
            res.save()
            messages.success(request, 'Reservation updated')
            return redirect('reservations:admin_reservation_list')

    return render(request, 'reservations/admin_reservation_form.html', {
        'form': form,
        'title': 'Edit Reservation',
        'slots': slots,
        'sel_date': sel_date,
        'editing': res,
        'min_date': today.isoformat(),
    })

@staff_member_required
def admin_reservation_delete(request, pk):
    # admin delete reservation
    res = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        res.delete()
        messages.success(request, 'Reservation deleted')
        return redirect('reservations:admin_reservation_list')
    return render(request, 'reservations/admin_confirm_delete.html', {
        'obj': res, 'type': 'reservation'
    })

@staff_member_required
def admin_user_list(request):
    # list users for admin
    users = User.objects.all()
    return render(request, 'reservations/admin_user_list.html', {'users': users})

@staff_member_required
def admin_user_add(request):
    # admin add user
    form = UserForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'User added')
        return redirect('reservations:admin_user_list')
    return render(request, 'reservations/admin_user_form.html', {
        'form': form, 'title': 'Add User'
    })

@staff_member_required
def admin_user_edit(request, pk):
    # admin edit user
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, 'User updated')
        return redirect('reservations:admin_user_list')
    return render(request, 'reservations/admin_user_form.html', {
        'form': form, 'title': 'Edit User'
    })

@staff_member_required
def admin_user_delete(request, pk):
    # admin delete user
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted')
        return redirect('reservations:admin_user_list')
    return render(request, 'reservations/admin_confirm_delete.html', {
        'obj': user, 'type': 'user'
    })
