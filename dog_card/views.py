from typing import Any
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from dog_card.models import DogCardModel
from rest_framework.response import Response
from dog_card.serializer import DogCardSerializer
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
# Create your views here.


class DogCardSearch(APIView):
    permission_classes = [AllowAny]

    def search_dogs_cards(self, *, name, size, gender):
        query = Q()
        if name:
            query &= Q(name__icontains=name)
        if size:
            query &= Q(size__icontains=size)
        if gender:
            query &= Q(gender__icontains=gender)
        if not any([name, size, gender]):
            return DogCardModel.objects.all()

        searched_cards = DogCardModel.objects.filter(query)
        return searched_cards

    def get(self, request):
        try:
            search_name = request.GET.get('name', '')
            search_size = request.GET.get('size', '')
            search_gender = request.GET.get('gender', '')

            searched_dogs_cards = self.search_dogs_cards(
                name=search_name, size=search_size, gender=search_gender)
            if searched_dogs_cards:
                serializers = DogCardSerializer(searched_dogs_cards, many=True)
                return Response({'Cards': serializers.data})
            else:
                return Response({'message': 'Карт не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['GET'])
# @csrf_exempt
# def search_dogs_cards(request):
#     try:
#         # Get the search parameters from the request
#         search_name = request.GET.get('name', '')
#         search_size = request.GET.get('size', '')
#         search_gender = request.GET.get('gender', '')
#         # Create a query object to filter the cards
#         query = Q()
#         if search_name:
#             query &= Q(name__icontains=search_name)
#         if search_size:
#             query &= Q(size__icontains=search_size)
#         if search_gender:
#             query &= Q(gender__icontains=search_gender)

#         searched_cards = DogCardModel.objects.filter(query)
#         # If there are cards, return them, otherwise return a message
#         if searched_cards:
#             serializers = DogCardSerializer(searched_cards, many=True)
#             return Response({'Cards': serializers.data})
#         else:
#             return Response({'message': 'Карт не знайдено'}, status=status.HTTP_404_NOT_FOUND)
#     except ValidationError as e:
#         return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
