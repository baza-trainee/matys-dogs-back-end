from rest_framework import status
from rest_framework.permissions import AllowAny
from dog_card.models import DogCardModel
from rest_framework.response import Response
from dog_card.serializer import DogCardSerializer
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from backblaze.models import FileModel
from backblaze.utils.b2_utils import converter_to_webP, delete_file_from_backblaze
from backblaze.utils.validation import image_validation
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from api.models import IsApprovedUser
# Create your views here.


class DogCardSearch(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [AllowAny]

    def search_dogs_cards(self, *, age, size, gender, ready_for_adoption):
        query = Q()
        if age:
            normilized_age = self.normalize_age(age)
            query &= Q(age__icontains=normilized_age)
        if size:
            query &= Q(size__icontains=size)
        if gender:
            query &= Q(gender__icontains=gender)
        if ready_for_adoption:
            query &= Q(ready_for_adoption__icontains=ready_for_adoption)
        if not any([age, size, gender, ready_for_adoption]):
            return DogCardModel.objects.all()

        searched_cards = DogCardModel.objects.filter(query)
        return searched_cards

    def normalize_age(self, age):
        # Replace common age-related terms to their Ukrainian equivalents
        # assuming 'years' and 'months' are provided in English by the users
        age = age.lower().replace('years', 'років').replace(
            'year', 'рік').replace('months', 'місяців').replace('month', 'місяць')
        age = ' '.join(age.split())
        return age

    @extend_schema(
        summary='Search dog cards',
        description="Search dog cards based on various criteria",

        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=False,
                description="Language code to get the content in a specific language (e.g., en, uk)",
                enum=["en", "uk"],
            ),
            OpenApiParameter(
                name='age', description='Search by dog age', required=False, type=str),
            OpenApiParameter(
                name='size', description='Search by dog size', required=False, type=str),
            OpenApiParameter(
                name='gender', description='Search by dog gender', required=False, type=str),
            OpenApiParameter(name='ready_for_adoption',
                             description='Search by dogs ready for adoption', required=False, type=bool),
        ],
        responses={
            200: DogCardSerializer(many=True),
            404: {'description': 'Жодних карт не знайдено відповідності критеріям'},
            500: {'description': 'Внутрішня помилка сервера'}
        }
    )
    def list(self, request):
        try:
            search_age = request.GET.get('age', '')
            search_size = request.GET.get('size', '')
            search_gender = request.GET.get('gender', '')
            serach_ready_for_adoption = request.GET.get(
                'ready_for_adoption', '')

            searched_dogs_cards = self.search_dogs_cards(
                age=search_age, size=search_size, gender=search_gender, ready_for_adoption=serach_ready_for_adoption)
            if searched_dogs_cards:
                serializers = DogCardSerializer(searched_dogs_cards, many=True)
                return Response({'Cards': serializers.data})
            else:
                return Response({'message': 'Карт не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DogCardView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated, IsApprovedUser]
    queryset = DogCardModel.objects.all()
    serializer_class = DogCardSerializer

    def update_dog_card(self, dog_card, data):
        for field, value in data.items():
            setattr(dog_card, field, value)
        dog_card.save()

    def handle_photo(self, request, dog_card):
        photo = request.FILES.get('photo')
        if photo:
            if dog_card.photo:
                dog_card.photo.delete()
                # assuming this deletes the file too
                delete_file_from_backblaze(dog_card.photo)
            image_validation(photo)
            webp_image_name, webp_image_id, bucket_name, _ = converter_to_webP(
                photo)
            image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
            return FileModel.objects.create(
                id=webp_image_id, name=webp_image_name, url=image_url, category='image'
            )
        return dog_card.photo

    @extend_schema(
        summary='List all dog cards',
        description="List all dog cards",
        responses={200: DogCardSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=False,
                description="Language code to get the content in a specific language (e.g., en, uk)",
                enum=["en", "uk"],
            ),]

    )
    def list(self, request):
        cards = DogCardModel.objects.all()
        serializer = DogCardSerializer(cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Create a new dog card',
        description="Create a new dog card",
        request=DogCardSerializer,
        responses={201: DogCardSerializer, 400: 'Bad Request'}
    )
    def create(self, request):
        try:
            data_fields = ['name', 'ready_for_adoption', 'gender', 'age', 'sterilization',
                           'vaccination_parasite_treatment', 'size', 'description']

            data = {field: request.data.get(field) for field in data_fields}
            temp_dog_card = DogCardModel()
            data['photo'] = self.handle_photo(request, temp_dog_card)

            # serialized_data = DogCardSerializer(data=data)
            # serialized_data.is_valid(raise_exception=True)

            dog_card = DogCardModel.objects.create(**data)
            dog_card_serializer = DogCardSerializer(instance=dog_card)

            return Response({'message': 'Карта створена', 'new_dogs_card': dog_card_serializer.data}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary='Update an existing dog card',
        description="Update an existing dog card",
        request=DogCardSerializer,
        responses={200: DogCardSerializer,
                   404: 'Dog card not found', 500: 'Internal Server Error'}
    )
    def update(self, request, pk):
        try:
            data_fields = ['name', 'ready_for_adoption', 'gender', 'age', 'sterilization',
                           'vaccination_parasite_treatment', 'size', 'description']
            data = {field: request.data.get(field) for field in data_fields}

            dog_card = DogCardModel.objects.get(pk=pk)
            data['photo'] = self.handle_photo(request, dog_card)

            self.update_dog_card(dog_card, data)

            dog_card_serializer = DogCardSerializer(dog_card)
            return Response({'message': 'Карта оновлена', 'updated_dog_card': dog_card_serializer.data},
                            status=status.HTTP_200_OK)
        except DogCardModel.DoesNotExist:
            return Response({'message': 'Карти не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary='Delete a dog card',
        description="Delete a dog card",
        responses={200: 'Dog card deleted',
                   404: 'Dog card not found', 500: 'Internal Server Error'}
    )
    def destroy(self, request, pk):
        try:
            card = DogCardModel.objects.get(id=pk)
            delete_file_from_backblaze(card.photo_id)
            card.delete()
            return Response({'message': 'Карта видалена'}, status=status.HTTP_200_OK)
        except DogCardModel.DoesNotExist:
            return Response({'message': 'Карти не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
