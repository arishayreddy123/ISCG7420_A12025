from django.contrib import admin
from django.urls import path, include
from reservations import views as res_views

urlpatterns = [
    # Public pages
    path('home/',     res_views.home,     name='home'),
    path('register/', res_views.register, name='register'),
    # Auth (login/logout)
    path('accounts/', include('django.contrib.auth.urls')),
    # Reservations app
    path('', include('reservations.urls', namespace='reservations')),
    # Admin site
    path('admin/', admin.site.urls),
]
