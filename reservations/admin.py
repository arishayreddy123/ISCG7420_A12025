from django.contrib import admin
from .models import Room, Reservation

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display  = ('name','location','capacity')
    search_fields = ('name','location')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display  = ('room','user','start_time','end_time')
    list_filter   = ('room','start_time')
    search_fields = ('user__username','room__name')
