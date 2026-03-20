"""
URL patterns for accounts app.
"""
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Profile
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),

    #units
    path("units/", views.units, name="units"),
    # Dashboard
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # Reset Password
    #path("reset-password/", views.reset_password_view, name="reset_password"),
]
