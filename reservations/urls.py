# reservations/urls.py
from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # map the site root to home
    path('', views.home, name='home'),

    # also keep /home/ if you like
    path('home/', views.home, name='home'),

    # user signup
    path('accounts/register/', views.register, name='register'),

    # list of rooms (for staff or browsing)
    path('rooms/', views.room_list, name='room_list'),

    # booking grid
    path('room-status/', views.room_status, name='room_status'),

    # reservation confirmation step
    path('confirm/<int:room_id>/', views.confirm_reservation, name='confirm_reservation'),

    # actually make a reservation
    path('reserve/<int:room_id>/', views.make_reservation, name='make_reservation'),

    # user’s own reservations
    path('my-reservations/', views.my_reservations, name='my_reservations'),

    # detail view
    path('detail/<int:res_id>/', views.reservation_detail, name='reservation_detail'),

    # edit an existing reservation
    path('edit/<int:res_id>/', views.edit_reservation, name='edit_reservation'),

    # cancel a reservation
    path('cancel/<int:res_id>/', views.cancel_reservation, name='cancel_reservation'),
]
