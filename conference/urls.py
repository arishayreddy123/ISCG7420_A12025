from django.contrib import admin
from django.urls import path, include
from reservations import views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Home page (about company)
    path('home/', views.home, name='home'),

    # Auth routes: login, logout
    path('accounts/', include('django.contrib.auth.urls')),

    # Registration form
    path('accounts/register/', views.register, name='register'),

    # Booking grid and reservation actions
    path('', include('reservations.urls', namespace='reservations')),
]
