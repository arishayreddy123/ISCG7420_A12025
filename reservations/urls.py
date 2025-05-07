from django.urls import path
from . import views

app_name = "reservations"

urlpatterns = [
    # List rooms & availability
    path('', views.room_status, name='room_status'),
    # Make a new reservation
    path('reserve/<int:room_id>/', views.make_reservation, name='make_reservation'),
    # See your bookings
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    # Edit or cancel an existing booking
    path('edit/<int:res_id>/', views.edit_reservation, name='edit_reservation'),
    path('cancel/<int:res_id>/', views.cancel_reservation, name='cancel_reservation'),
]
