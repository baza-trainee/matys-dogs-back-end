from django.urls import path
from main_page.views import MainPageView, NewsView, PartnersView


urlpatterns = [
    path("", MainPageView.as_view({"get": "list"}), name="MainPageView"),
    path(
        "news",
        NewsView.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="news",
    ),
    path(
        "news/<int:pk>",
        NewsView.as_view({"put": "update", "delete": "destroy"}),
        name="news",
    ),
    path(
        "partners",
        PartnersView.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="partners",
    ),
    path("partners/<int:pk>", PartnersView.as_view({"delete": "destroy"})),
]
