from django.urls import path
from about.views import AboutList, AboutImages, AboutEmployment

urlpatterns = [
    path("about-us", AboutList.as_view({"get": "list"}), name="about"),
    path(
        "about/images",
        AboutImages.as_view({"get": "list", "post": "create"}),
        name="about-images",
    ),
    path(
        "about/images/<str:pk>",
        AboutImages.as_view({"delete": "destroy"}),
        name="about-images",
    ),
    path(
        "about/employment",
        AboutEmployment.as_view({"get": "list", "put": "update"}),
        name="about-employment",
    ),
]
