from django.urls import path
from about.views import AboutList, About
urlpatterns = [
    path('about-us', AboutList.as_view(), name="about"),
    path('about', About.as_view(), name="About")
]
