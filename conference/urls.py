from django.contrib import admin
from django.urls import path, include
from reservations import views as res_views

urlpatterns = [
    path('home/',     res_views.home,     name='home'),
    path('register/', res_views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('reservations.urls', namespace='reservations')),
    path('admin/', admin.site.urls),  # ← admin site
]
