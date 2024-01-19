from django.urls import path
from dog_card.views import DogCardSearch

urlpatterns = [
    path('catalog/', DogCardSearch.as_view(), name='search_dogs_cards')
]
