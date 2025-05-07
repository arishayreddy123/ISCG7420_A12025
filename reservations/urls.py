from django.urls import path
from . import views

app_name = "reservations"

urlpatterns = [
    # availability grid
    path('', views.room_status, name='room_status'),
    # confirmation step before booking
    path('confirm/<int:room_id>/', views.confirm_reservation, name='confirm_reservation'),
    # final booking action
    path('reserve/<int:room_id>/', views.make_reservation, name='make_reservation'),
    # list my bookings
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    # edit & cancel
    path('edit/<int:res_id>/', views.edit_reservation, name='edit_reservation'),
    path('cancel/<int:res_id>/', views.cancel_reservation, name='cancel_reservation'),
]
