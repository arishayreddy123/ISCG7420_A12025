from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Reservation

User = get_user_model()

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time':   forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class RegistrationForm(UserCreationForm):
    class Meta:
        model  = User
        fields = ('username','email','password1','password2')
