from django.urls import path
from about.views import about, About
urlpatterns = [
    path('about-us', about, name="about"),
    path('about', About.as_view(), name="About")
]
