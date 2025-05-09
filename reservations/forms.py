from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Reservation

# ─── RegistrationForm for public signup ────────────────────────────────────────
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email address'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

# ─── RoomForm for admin room create/edit ──────────────────────────────────────
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'description']

# ─── ReservationForm for booking ──────────────────────────────────────────────
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['room', 'user', 'start_time', 'end_time']

# ─── UserForm for admin editing existing users ───────────────────────────────
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'is_active']
