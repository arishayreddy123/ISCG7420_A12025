from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # ─── Public ───────────────────────────────────────────────────────────────
    path('home/',                   views.home,                   name='home'),
    path('register/',               views.register,               name='register'),

    # ─── Room browsing & booking ─────────────────────────────────────────────
    path('rooms/',                  views.room_list,              name='room_list'),
    path('room-status/',            views.room_status,            name='room_status'),

    # confirmation step (show start/end, ask “Confirm?”)
    path('confirm/<int:room_id>/',  views.confirm_reservation,    name='confirm_reservation'),

    # final reservation creation
    path('reserve/<int:room_id>/',  views.make_reservation,       name='make_reservation'),

    # ─── My reservations ─────────────────────────────────────────────────────
    path('my-reservations/',           views.my_reservations,       name='my_reservations'),
    path('reservation/<int:res_id>/',  views.reservation_detail,    name='reservation_detail'),
    path('reservation/<int:res_id>/edit/',   views.edit_reservation,  name='edit_reservation'),
    path('reservation/<int:res_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),

    # ─── Admin: Rooms ─────────────────────────────────────────────────────────
    path('admin/rooms/',               views.admin_room_list,      name='admin_room_list'),
    path('admin/rooms/add/',           views.admin_room_add,       name='admin_room_add'),
    path('admin/rooms/<int:pk>/edit/', views.admin_room_edit,      name='admin_room_edit'),
    path('admin/rooms/<int:pk>/delete/', views.admin_room_delete,   name='admin_room_delete'),

    # ─── Admin: Reservations ──────────────────────────────────────────────────
    path('admin/reservations/',               views.admin_reservation_list,   name='admin_reservation_list'),
    path('admin/reservations/add/',           views.admin_reservation_add,    name='admin_reservation_add'),
    path('admin/reservations/<int:pk>/edit/', views.admin_reservation_edit,   name='admin_reservation_edit'),
    path('admin/reservations/<int:pk>/delete/', views.admin_reservation_delete, name='admin_reservation_delete'),

    # ─── Admin: Users ─────────────────────────────────────────────────────────
    path('admin/users/',               views.admin_user_list,      name='admin_user_list'),
    path('admin/users/add/',           views.admin_user_add,       name='admin_user_add'),
    path('admin/users/<int:pk>/edit/', views.admin_user_edit,      name='admin_user_edit'),
    path('admin/users/<int:pk>/delete/', views.admin_user_delete,   name='admin_user_delete'),
]
