from django.urls import path
from dog_card.views import DogCardSearch, DogCardView

urlpatterns = [
    path("catalog/", DogCardSearch.as_view({"get": "list"}), name="search_dogs_cards"),
    path(
        "dog_card",
        DogCardView.as_view({"get": "list", "post": "create"}),
        name="dog_card",
    ),
    path(
        "dog_card/<int:pk>",
        DogCardView.as_view({"put": "update", "delete": "destroy"}),
        name="dog_card",
    ),
]
