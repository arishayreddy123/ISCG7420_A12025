# conference/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    # redirect root “/” to reservations:home
    path(
        "",
        RedirectView.as_view(pattern_name="reservations:home", permanent=False),
        name="root-redirect"
    ),

    # all reservations‑app URLs under /manage/
    path("manage/", include("reservations.urls", namespace="reservations")),

    # Django admin
    path("admin/", admin.site.urls),

    # Auth: login & logout
    path(
      "accounts/login/",
      auth_views.LoginView.as_view(template_name="registration/login.html"),
      name="login"
    ),
    path(
      "accounts/logout/",
      auth_views.LogoutView.as_view(next_page="reservations:home"),
      name="logout"
    ),

    path("accounts/", include("django.contrib.auth.urls")),
]
