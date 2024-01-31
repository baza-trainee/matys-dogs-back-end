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

    def age_years(self, *, lower_bound, upper_bound):
        possible_ages = []
        lower_bound_years = max(1, lower_bound / 12)
        upper_bound_years = upper_bound / 12
        age_years = lower_bound_years
        while age_years <= upper_bound_years:
            if age_years <= 3:
                if age_years == 1:
                    year_str = "рік"
                elif 1 < age_years <= 4 or (age_years % 1 == 0.5 and age_years < 5):
                    year_str = "роки"

                if age_years % 1 == 0:
                    year_num = f'{int(age_years)}'
                else:
                    year_num = f"{age_years:.1f}".replace(".", ",")
                possible_ages.append(
                    f'{year_num} {year_str}')
                age_years += 0.5
            elif age_years > 3:
                if age_years < 5:
                    year_str = "роки"
                else:
                    year_str = "років"
                if age_years % 1 == 0:
                    year_num = f'{int(age_years)}'
                else:
                    year_num = f"{age_years:.1f}".replace(
                        ".", ",")
                possible_ages.append(
                    f'{year_num} {year_str}')
                age_years += 0.5
        return possible_ages

    def age_in_months(self, *,  lower_bound, upper_bound):
        """
        Generates a list of age strings in months and years between the specified bounds.

        Args:
        lower_bound (float): The lower bound of age in months.
        upper_bound (float): The upper bound of age in months.

        Returns:
        list: A list of age strings in months and years.
        """
        possible_ages = []

        age_months = lower_bound
        while age_months <= upper_bound:
            if age_months <= 12:
                if age_months in [1, 2, 3, 4]:
                    month_str = "місяць" if age_months == 1 else 'місяці'
                else:
                    month_str = "місяців"
                age_str = f"{age_months:.1f}" if age_months % 1 else f"{int(age_months)}"
                possible_ages.append(f'{age_str} {month_str}')
                if age_months == 12:
                    possible_ages.append(f'1 рік')
                age_months += 0.5

        return possible_ages

    def get_age_range(self, *, age_category):
        age_ranges = {
            'щеня': (0, 12),
            'puppy': (0, 12),
            'молодий': (12, 36),
            'young': (12, 36),
            'дорослий': (42, 240),
            'adult': (42, 240),
        }
        lower_bound, upper_bound = age_ranges.get(age_category, (0, 0))
        if lower_bound < 12:
            return self.age_in_months(lower_bound=lower_bound, upper_bound=upper_bound)
        elif lower_bound >= 12:
            return self.age_years(lower_bound=lower_bound, upper_bound=upper_bound)

    def search_dogs_cards(self, *, age, size, gender, ready_for_adoption):
        query = Q()
        if age:
            age_range = self.get_age_range(age_category=age)
            query &= Q(age_uk__in=age_range)
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
                name='age',
                description='Search by dog age',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=[
                    'щеня',
                    'молодий',
                    'дорослий',
                    'puppy',
                    'young',
                    'adult']),
            OpenApiParameter(
                name='size',
                description='Search by dog size',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=[
                    'small',
                    'medium',
                    'large',
                    'маленький',
                    'середній',
                    'великий'
                ]
            ),
            OpenApiParameter(
                name='gender',
                description='Search by dog gender',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=[
                    'male',
                    'female',
                    'хлопчик',
                    'дівчинка'
                ]
            ),
            OpenApiParameter(name='ready_for_adoption',
                             description='Search by dogs ready for adoption', required=False, type=bool),
        ],
        responses={
            200: DogCardSerializer(many=True),
            400: {'description': 'Жодних карт не знайдено відповідності критеріям'},
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
                return Response({'message': 'Карт не знайдено'}, status=status.HTTP_400_BAD_REQUEST)
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
