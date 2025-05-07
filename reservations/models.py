from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Room(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    location    = models.CharField(max_length=200, blank=True)
    capacity    = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.capacity})"

class Reservation(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    room       = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time   = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.room.name}: {self.start_time:%Y-%m-%d %H:%M}"
