from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Room, Reservation

# — Customize admin site titles —
admin.site.site_header  = "Conference Booking Admin"
admin.site.site_title   = "Conference Admin"
admin.site.index_title  = "Administrator Dashboard"

# — Manage user accounts (5.5) —
User = get_user_model()
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display   = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter    = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields  = ('username', 'email', 'first_name', 'last_name')
    ordering       = ('username',)

# — Inline reservations under each room so admin can cancel or view (5.3) —
class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0
    readonly_fields = ('user', 'start_time', 'end_time', 'created_at')
    can_delete = True

# — Manage rooms (5.1) —
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display   = ('name', 'location', 'capacity')
    search_fields  = ('name', 'location')
    list_filter    = ('capacity',)
    ordering       = ('name',)
    inlines        = [ReservationInline]

# — Manage all reservations (5.2, 5.3, 5.4) —
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display      = ('room', 'user', 'start_time', 'end_time', 'created_at')
    list_filter       = ('room', 'user', 'start_time')
    search_fields     = ('room__name', 'user__username')
    date_hierarchy    = 'start_time'
    ordering          = ('-start_time',)
    autocomplete_fields = ('user', 'room')
