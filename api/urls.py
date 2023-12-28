from . import views
from django.urls import path, include

urlpatterns = [
    path('login', views.login, name='login'),
    path('', views.home, name='home')
]
