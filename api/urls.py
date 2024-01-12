from . import views
from django.urls import path

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('reset-passoword', views.reset_password, name='reset_password'),
    path('forgot-password', views.forgot_password, name='forgot_password'),
]
