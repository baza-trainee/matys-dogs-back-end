from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from dog_card.models import DogCardModel
from rest_framework.response import Response
from dog_card.serializer import DogCardSerializer


# Create your views here.

@api_view(['GET'])
@csrf_exempt
def get_dogs_cards(request):
    getAllCards = DogCardModel.objects.all()
    serializers = DogCardSerializer(getAllCards, many=True)
    return Response({'dogs': serializers.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@csrf_exempt
def search_get_dogs_cards(request, params):
    pass
