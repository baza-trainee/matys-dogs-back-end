from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from dog_card.models import DogCardModel
from rest_framework.response import Response
from dog_card.serializer import DogCardSerializer
from django.db.models import Q

# Create your views here.


@api_view(['GET'])
@csrf_exempt
def search_dogs_cards(request):
    # Get the search parameters from the request
    search_name = request.GET.get('name', '')
    search_size = request.GET.get('size', '')
    search_gender = request.GET.get('gender', '')
    print(search_name, search_size, search_gender)
    # Create a query object to filter the cards
    query = Q()
    if search_name:
        query &= Q(name__icontains=search_name)
    if search_size:
        query &= Q(size__icontains=search_size)
    if search_gender:
        query &= Q(gender__icontains=search_gender)

    searched_cards = DogCardModel.objects.filter(query)
    # If there are cards, return them, otherwise return a message
    if searched_cards:
        serializers = DogCardSerializer(searched_cards, many=True)
        return Response({'message': serializers.data})
    else:
        return Response({'message': 'Карт не знайдено'}, status=status.HTTP_200_OK)
