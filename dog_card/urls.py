from django.urls import path
from dog_card.views import get_dogs_cards

urlpatterns = [
    path('dogs-cards', get_dogs_cards, name='dogs_cards'),
]
