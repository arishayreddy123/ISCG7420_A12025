from django import forms
from django.contrib.auth.models import User
from .models import Room, Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['start_time', 'end_time']

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'description']

class ReservationAdminForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['user', 'room', 'start_time', 'end_time']

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff', 'is_active']
