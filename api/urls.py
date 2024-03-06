from django.urls import path
from .views import AuthenticationService, AdminService

urlpatterns = [
    path("login", AuthenticationService.as_view({"post": "login"}), name="login"),
    path(
        "register", AuthenticationService.as_view({"post": "register"}), name="register"
    ),
    path(
        "reset-password/<str:uidb64>/<str:token>",
        AuthenticationService.as_view({"post": "reset_password"}),
        name="reset_password",
    ),
    path(
        "forgot-password",
        AuthenticationService.as_view({"post": "forgot_password"}),
        name="forgot_password",
    ),
    path("admins", AdminService.as_view({"get": "list"})),
    path("admins/<int:pk>", AdminService.as_view({"put": "update"})),
    path("is_auth", AuthenticationService.as_view({"get": "is_Auth"}), name="is_auth"),
]
