from django.urls import path
from about.views import about
urlpatterns = [
    path('about', about, name="about")
]
