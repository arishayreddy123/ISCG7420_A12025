from django.contrib import admin
from .models import Room, Reservation

class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0
    readonly_fields = ('user', 'start_time', 'end_time', 'created_at')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display    = ('name', 'location', 'capacity')
    search_fields   = ('name', 'location')
    list_filter     = ('capacity',)
    ordering        = ('name',)
    inlines         = [ReservationInline]  # show reservations under each room

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display    = ('room', 'user', 'start_time', 'end_time', 'created_at')
    list_filter     = ('room', 'user', 'start_time')
    search_fields   = ('room__name', 'user__username')
    date_hierarchy  = 'start_time'
    ordering        = ('-start_time',)
