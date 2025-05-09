# reservations/admin_urls.py
from django.urls import path
from . import views

app_name = 'manage'

urlpatterns = [
    # Rooms
    path('rooms/',        views.admin_room_list,   name='room_list'),
    path('rooms/add/',    views.admin_room_add,    name='room_add'),
    path('rooms/<int:pk>/edit/',   views.admin_room_edit,   name='room_edit'),
    path('rooms/<int:pk>/delete/', views.admin_room_delete, name='room_delete'),

    # Reservations
    path('reservations/',        views.admin_reservation_list,   name='reservation_list'),
    path('reservations/add/',    views.admin_reservation_add,    name='reservation_add'),
    path('reservations/<int:pk>/edit/',   views.admin_reservation_edit,   name='reservation_edit'),
    path('reservations/<int:pk>/delete/', views.admin_reservation_delete, name='reservation_delete'),

    # Users
    path('users/',        views.admin_user_list,   name='user_list'),
    path('users/add/',    views.admin_user_add,    name='user_add'),
    path('users/<int:pk>/edit/',   views.admin_user_edit,   name='user_edit'),
    path('users/<int:pk>/delete/', views.admin_user_delete, name='user_delete'),
]
