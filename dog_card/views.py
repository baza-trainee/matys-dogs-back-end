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
def get_dogs_cards(request):
    getAllCards = DogCardModel.objects.all()
    serializers = DogCardSerializer(getAllCards, many=True)
    return Response({'dogs': serializers.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@csrf_exempt
def search_dogs_cards(request, params):
    search_name = request.GET.get('name', '')
    search_size = request.GET.get('size', '')
    serch_gender = request.GET.get('gender', '')
    # search_is_cheapted = request.GET.get('is_cheapred', '')
    searchedCards = DogCardModel.objects.filter(Q(name__icontains=search_name) & Q(
        size__icontains=search_size) & Q(gender__icontains=serch_gender))

    if not searchedCards.exists():
        return Response({'message': 'No cards found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        serializers = DogCardSerializer(searchedCards, many=True)
    return Response({'message': serializers.data})
