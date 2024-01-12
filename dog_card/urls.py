from django.urls import path
from dog_card.views import search_dogs_cards

urlpatterns = [
    path('catalog/', search_dogs_cards, name='search_dogs_cards')
]
