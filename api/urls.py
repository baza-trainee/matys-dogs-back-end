from . import views
from django.urls import path, include

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('', views.home, name='home')
]
