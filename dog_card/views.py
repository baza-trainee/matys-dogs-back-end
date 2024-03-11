from rest_framework import status, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from dog_card.models import DogCardModel
from rest_framework.response import Response
from dog_card.serializer import DogCardSerializer, DogCardTranslationSerializer
from django.db.models import Q
from api.models import IsApprovedUser
from backblaze.models import FileModel
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import GenericViewSet
from backblaze.utils.b2_utils import converter_to_webP, delete_file_from_backblaze
from drf_spectacular.types import OpenApiTypes
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)


# Create your views here.


class DogCardSearch(mixins.ListModelMixin, GenericViewSet):
    """
    A viewset that provides list operations for searching DogCardModel instances
    based on age, size, gender, and adoption status.
    """

    permission_classes = [AllowAny]

    def age_years(self, *, lower_bound, upper_bound):
        """
        Generates a list of age descriptions in years from lower_bound to upper_bound.

        The method accounts for language specifics related to age descriptions,
        providing appropriate suffixes based on the age.

        Args:
            lower_bound (int): The minimum age in months to include in the age range.
            upper_bound (int): The maximum age in months to include in the age range.

        Returns:
            list: A list of strings describing ages in years, adjusted for language nuances.
        """
        possible_ages = []
        lower_bound_years = max(1, lower_bound / 12)
        upper_bound_years = upper_bound / 12

        age_years = lower_bound_years
        while age_years <= upper_bound_years:
            if age_years == 1:
                year_str = "рік"
            elif 1 < age_years < 5 or (age_years % 1 == 0.5 and age_years <= 4.5):
                year_str = "роки"
            else:
                year_str = "років"

            year_num = (
                f"{int(age_years)}"
                if age_years % 1 == 0
                else f"{age_years:.1f}".replace(".", ",")
            )

            possible_ages.append(f"{year_num} {year_str}")

            age_years += 0.5
        return possible_ages

    def age_in_months(self, *, lower_bound, upper_bound):
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
            if age_months in [1, 2, 3, 4]:
                month_str = "місяць" if age_months == 1 else "місяці"
            else:
                month_str = "місяців"

                age_str = (
                    f"{age_months:.1f}" if age_months % 1 else f"{int(age_months)}"
                )
                possible_ages.append(f"{age_str} {month_str}")

            age_months += 0.5
        if upper_bound >= 12 and "1 рік" not in possible_ages:
            possible_ages.append("1 рік")
        return possible_ages

    def get_age_range(self, *, age_category):
        """
        Determines the age range for a given age category and generates age descriptions
        either in months or years based on the category.

        Args:
            age_category (str): A string representing the age category of the dog. Expected values
                                include 'щеня' (puppy), 'молода собака' (young dog), and 'доросла собака' (adult dog),
                                with their English equivalents.

        Returns:
            list: A list of strings representing age descriptions within the specified range.
                The descriptions are in months for puppies and in years for older dogs.
        """
        age_ranges = {
            "щеня": (0, 12),
            "puppy": (0, 12),
            "молода собака": (12, 36),
            "young dog": (12, 36),
            "доросла собака": (42, 240),
            "adult dog": (42, 240),
        }

        lower_bound, upper_bound = age_ranges.get(age_category, (0, 0))
        # Generate age descriptions based on whether the age range falls below or above 12 months
        if lower_bound < 12:
            return self.age_in_months(lower_bound=lower_bound, upper_bound=upper_bound)
        elif lower_bound >= 12:
            return self.age_years(lower_bound=lower_bound, upper_bound=upper_bound)

    def search_dogs_cards(self, *, age, size, gender, ready_for_adoption):
        """
        Constructs a query to search for DogCardModel instances based on specified criteria.

        Args:
            age (str): Age category to filter by.
            size (str): Size category to filter by.
            gender (str): Gender to filter by.
            ready_for_adoption (str): Adoption readiness to filter by, expects 'true' or 'false'.

        Returns:
            QuerySet: A queryset of filtered DogCardModel instances.
        """
        query = Q()
        if age:
            age_range = self.get_age_range(age_category=age)
            query &= Q(age_uk__in=age_range)
        if size:
            # Assuming exact match is more appropriate
            query &= Q(size__icontains=size)
        if gender:
            # Assuming exact match is more appropriate
            query &= Q(gender__icontains=gender)
        if ready_for_adoption:
            query &= Q(ready_for_adoption__icontains=ready_for_adoption)
        if not any([age, size, gender, ready_for_adoption]):
            return DogCardModel.objects.all()

        searched_cards = DogCardModel.objects.filter(query).prefetch_related("photo")
        return searched_cards

    @extend_schema(
        summary="Search dog cards based on various criteria",
        description="Performs a search across dog cards using filters like age, size, gender, and adoption status.",
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=False,
                description="Specify the language for content localization.",
                enum=["en", "uk"],
            ),
            OpenApiParameter(
                name="age",
                description='Filter by age category. Supported values are "puppy", "young dog", "adult dog" and their Ukrainian equivalents.',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=[
                    "щеня",
                    "молода собака",
                    "доросла собака",
                    "puppy",
                    "young dog",
                    "adult dog",
                ],
            ),
            OpenApiParameter(
                name="size",
                description='Filter by size category. Supported values are "small", "medium", "large" and their Ukrainian equivalents.',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=["small", "medium", "large", "маленький", "середній", "великий"],
            ),
            OpenApiParameter(
                name="gender",
                description='Filter by gender. Supported values are "boy", "girl" and their Ukrainian equivalents.',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=["boy", "girl", "хлопчик", "дівчинка"],
            ),
            OpenApiParameter(
                name="ready_for_adoption",
                description='Filter by adoption readiness status. Expected boolean values "true" or "false".',
                required=False,
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: DogCardSerializer(many=True),
            400: {"message": "Карт не знайдено"},
        },
    )
    def list(self, request, *args, **kwargs):
        """
        Overrides the default list method to incorporate search functionality based on query parameters.
        """
        try:
            search_age = request.GET.get("age", "")
            search_size = request.GET.get("size", "")
            search_gender = request.GET.get("gender", "")
            serach_ready_for_adoption = request.GET.get("ready_for_adoption", "")

            searched_dogs_cards = self.search_dogs_cards(
                age=search_age,
                size=search_size,
                gender=search_gender,
                ready_for_adoption=serach_ready_for_adoption,
            )
            if searched_dogs_cards:
                serializers = DogCardSerializer(searched_dogs_cards, many=True)
                return Response(serializers.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "Карт не знайдено"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception:
            return Response(
                {"message": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DogCardView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    ViewSet for handling CRUD operations for DogCardModel instances.
    Allows listing, creating, updating, and deleting dog cards.

    Attributes:
        permission_classes: Enforces authentication and user approval.
        parser_classes: Handles multipart form data for file uploads.
        queryset: The base queryset for dog card operations.
        serializer_class: The serializer for input and output operations.
    """

    permission_classes = [IsAuthenticated, IsApprovedUser]
    parser_classes = [MultiPartParser, FormParser]
    queryset = DogCardModel.objects.all().prefetch_related("photo")
    serializer_class = DogCardTranslationSerializer

    def update_dog_card(self, dog_card, data):
        """
        Updates a DogCardModel instance with given data.

        Args:
            dog_card: The DogCardModel instance to update.
            data: A dictionary of fields to update on the DogCardModel instance.
        """
        for field, value in data.items():
            setattr(dog_card, field, value)
        dog_card.save()

    def perform_create(self, serilaizer):
        """
        Saves the serializer when creating a new instance.

        Args:
            serializer: The serializer containing the validated data.
        """
        serilaizer.save()

    def handle_photo(self, photo, dog_card):
        """
        Handles the photo upload process for a DogCardModel instance.

        Args:
            request: The HTTP request containing the photo file in FILES.
            dog_card: The DogCardModel instance to associate with the photo.

        Returns:
            A FileModel instance representing the uploaded photo.
        """
        if not photo:
            return None
        if dog_card and dog_card.photo:
            dog_card.photo.delete()
            delete_file_from_backblaze(dog_card.photo_id)

        webp_image_name, webp_image_id, image_url = converter_to_webP(photo)
        return FileModel.objects.create(
            id=webp_image_id, name=webp_image_name, url=image_url, category="image"
        )

    @extend_schema(
        summary="Retrieve a list of all dog cards",
        description="Provides a list of all available dog cards in the system with detailed information.",
        responses={200: DogCardSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=False,
                description="Specify the language of the content returned. Defaults to English.",
                enum=["en", "uk"],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """
        Lists all DogCardModel instances.

        Overrides the default list method to provide custom functionality.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new dog card",
        description="Allows the creation of a new dog card with the provided details including an optional photo.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "name_en": {"type": "string"},
                    "ready_for_adoption": {"type": "boolean"},
                    "gender": {
                        "type": "string",
                        "enum": ["хлопчик", "дівчинка"],
                        "description": "Gender of the dog",
                    },
                    "gender_en": {
                        "type": "string",
                        "enum": ["boy", "girl"],
                        "description": "Gender of the dog",
                    },
                    "age": {
                        "type": "string",
                        "description": "Age of the dog",
                    },
                    "age_en": {
                        "type": "string",
                        "description": "Age of the dog",
                    },
                    "sterilization": {"type": "boolean"},
                    "vaccination_parasite_treatment": {"type": "boolean"},
                    "size": {
                        "type": "string",
                        "enum": ["маленький", "середній", "великий"],
                        "description": "Size of the dog",
                    },
                    "size_en": {
                        "type": "string",
                        "enum": [
                            "small",
                            "medium",
                            "large",
                        ],
                        "description": "Size of the dog",
                    },
                    "description": {"type": "string"},
                    "description_en": {"type": "string"},
                    "photo": {"type": "string", "format": "binary"},
                },
                "required": [
                    "name",
                    "ready_for_adoption",
                    "gender",
                    "age",
                    "size",
                    "description",
                    "photo",
                ],
            }
        },
        responses={
            201: DogCardTranslationSerializer,
            400: {"description": "Помилка при створені ValidationError"},
            500: {"description": "Помилка сервера"},
        },
    )
    def create(self, request):
        """
        Creates a new DogCardModel instance.

        Handles the photo file separately, using the handle_photo method to process it.
        """
        try:
            serilaizer = self.get_serializer(
                data=request.data, context={"request": request, "view": self}
            )
            serilaizer.is_valid(raise_exception=True)
            self.perform_create(serilaizer)
            return Response(
                serilaizer.data,
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                {"description": f"Помилка при створені {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Update a dog card",
        description="Updates the details of an existing dog card identified by the given primary key.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "name_en": {"type": "string"},
                    "ready_for_adoption": {"type": "boolean"},
                    "gender": {
                        "type": "string",
                        "enum": ["хлопчик", "дівчинка"],
                        "description": "Gender of the dog",
                    },
                    "gender_en": {
                        "type": "string",
                        "enum": ["boy", "girl"],
                        "description": "Gender of the dog",
                    },
                    "age": {
                        "type": "string",
                        "description": "Age of the dog",
                    },
                    "age_en": {
                        "type": "string",
                        "description": "Age of the dog",
                    },
                    "sterilization": {"type": "boolean"},
                    "vaccination_parasite_treatment": {"type": "boolean"},
                    "size": {
                        "type": "string",
                        "enum": ["маленький", "середній", "великий"],
                        "description": "Size of the dog",
                    },
                    "size_en": {
                        "type": "string",
                        "enum": [
                            "small",
                            "medium",
                            "large",
                        ],
                        "description": "Size of the dog",
                    },
                    "description": {"type": "string"},
                    "description_en": {"type": "string"},
                    "photo": {"type": "string", "format": "binary"},
                },
            }
        },
        responses={
            200: DogCardTranslationSerializer,
            400: {"description": "Помилка при оновлені ValidationError"},
            404: {"description": "Карта не знайдена"},
            500: {"description": "Помилка сервера"},
        },
    )
    def update(self, request, pk):
        """
        Updates an existing DogCardModel instance.

        Args:
            request: The HTTP request object containing the update data.
            pk: The primary key of the DogCardModel instance to update.

        Returns a response indicating the outcome of the update operation.
        """
        try:
            dog_card = DogCardModel.objects.get(pk=pk)
            serializer = self.get_serializer(
                dog_card, data=request.data, context={"request": request, "view": self}
            )
            serializer.is_valid(raise_exception=True)
            self.update_dog_card(dog_card, serializer.validated_data)
            self.perform_update(serializer=serializer)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                {"description": f"Помилка при оновлені {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DogCardModel.DoesNotExist:
            return Response(
                {"description": "Карта не знайдена"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Delete a dog card",
        description="Permanently removes a dog card from the system, including its associated photo from external storage.",
        responses={
            200: {"description": "Карта видалена"},
            404: {"description": "Карти не знайдено"},
            500: {"description": "Помилка сервера"},
        },
    )
    def destroy(self, request, pk):
        """
        Deletes a DogCardModel instance along with its associated photo.

        Args:
            request: The HTTP request object.
            pk: The primary key of the DogCardModel instance to delete.

        Returns a response indicating the outcome of the deletion operation.
        """
        try:
            card = DogCardModel.objects.get(pk=pk)
            if card.photo:
                delete_file_from_backblaze(card.photo_id)
            card.photo.delete()
            card.delete()
            return Response(
                {"description": "Карта видалена"}, status=status.HTTP_200_OK
            )
        except DogCardModel.DoesNotExist:
            return Response(
                {"description": "Карти не знайдено"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"description": f"Помилка сервера {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
