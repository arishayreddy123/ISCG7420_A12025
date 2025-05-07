from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Room(models.Model):
    name        = models.CharField(max_length=100)
    location    = models.CharField(max_length=200)
    capacity    = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    room        = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    created_at  = models.DateTimeField(auto_now_add=True)  # ← new field

    def __str__(self):
        return f"{self.room.name} by {self.user.username}"
