from django.urls import path
from .views import AuthenticationService

urlpatterns = [
    path('login', AuthenticationService.as_view({'post': 'login'}), name='login'),
    path('register', AuthenticationService.as_view({'post': 'register'}), name='register'),
    path('reset-passoword/<uidb64>/<token>',AuthenticationService.as_view({'post': 'reset_password'}), name='reset_password'),
    path('forgot-password', AuthenticationService.as_view({'post': 'forgot_password'}), name='forgot_password'),
]

