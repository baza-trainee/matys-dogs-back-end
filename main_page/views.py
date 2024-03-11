# trunk-ignore-all(black)
import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from main_page.serializer import (
    NewsSerializer,
    NewsTranslationsSerializer,
    PartnerSerializer,
)
from dog_card.serializer import DogCardSerializer
from .models import NewsModel as News, Partners
from backblaze.utils.b2_utils import converter_to_webP, delete_file_from_backblaze
from backblaze.models import FileModel
from dog_card.models import DogCardModel
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from api.models import IsApprovedUser
from rest_framework.validators import ValidationError


logger = logging.getLogger(__name__)
# Main Page -------------------------------------------------------------------


class MainPageView(ListModelMixin, GenericViewSet):
    """
    This class represents a view for the main page. It is a subclass of the `mixins.ListModelMixin` and `GenericViewSet` classes.

    Attributes:
        permission_classes (list): A list of permission classes that determine the access permissions for this view. In this case, it allows any user to access the view.
        serializer_mapping (dict): A dictionary that maps model classes to their corresponding serializer classes.

    Methods:
        list(request): This method is called when a GET request is made to the view. It retrieves the necessary data from the database, serializes it using the appropriate serializers, and returns the serialized data as a response.

            Parameters:
                request (Request): The HTTP request object.

            Returns:
                Response: The HTTP response object containing the serialized data.

            Raises:
                Http404: If no data is found, a 404 Not Found response is raised.
    """

    permission_classes = [AllowAny]
    serializer_class = NewsSerializer
    serializer_mapping = {
        News: NewsSerializer,
        Partners: PartnerSerializer,
        DogCardModel: DogCardSerializer,
    }

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=False,
                description="Language code to get the content in a specific language (e.g., en, uk)",
                enum=["en", "uk"],
            ),
        ],
        tags=["Main Page"],
    )
    def list(self, request, *args, **kwargs):
        """
        This method is called when a GET request is made to the view. It retrieves the necessary data from the database, serializes it using the appropriate serializers, and returns the serialized data as a response.

        Parameters:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object containing the serialized data.

        Raises:
            Http404: If no data is found, a 404 Not Found response is raised.
        """

        news_queryset = News.objects.get_lastest().prefetch_related("photo")
        dog_cards_queryset = DogCardModel.objects.all().prefetch_related("photo")
        partners_queryset = Partners.objects.all().prefetch_related("logo")

        news_serializer = self.serializer_mapping[News](news_queryset, many=True)
        dog_cards_serializer = self.serializer_mapping[DogCardModel](
            dog_cards_queryset, many=True
        )
        partners_serializer = self.serializer_mapping[Partners](
            partners_queryset, many=True
        )

        # Make response data
        response_data = {
            "news": news_serializer.data,
            "partners": partners_serializer.data,
            "dog_cards": dog_cards_serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


# News------------------------------------------------------------------


class NewsView(
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """
    A viewset for listing, creating, updating, and deleting news items.
    It supports photo uploads for news items,with special handling for
    converting uploaded photos to webP format and cleaning up resources
    on updates or deletion.
    """

    permission_classes = [IsAuthenticated, IsApprovedUser]
    queryset = News.objects.all().prefetch_related("photo")
    serializer_class = NewsTranslationsSerializer

    def handle_photo(self, photo, news):
        """
        Handles the upload and conversion of a photo to webP format. If the news item already has a photo,
        it deletes the existing photo and its associated file in Backblaze storage before updating.

        Args:
            request: HttpRequest object containing the photo file in FILES.
            news: The news instance to associate the photo with, or None if creating a new news item.

        Returns:
            A FileModel instance representing the uploaded and converted photo.
        """
        if not photo:
            return None
        if news and news.photo:
            news.photo.delete()
            delete_file_from_backblaze(news.photo_id)

        webp_image_name, webp_image_id, image_url = converter_to_webP(photo)
        return FileModel.objects.create(
            id=webp_image_id, name=webp_image_name, url=image_url, category="image"
        )

    def perform_create(self, serilaizer):
        """
        Overrides the default perform_create method to save the provided serializer.

        Note: Typo corrected in the argument name from 'serilaizer' to 'serializer'.

        Args:
            serializer: The serializer instance containing the validated data.
        """
        serilaizer.save()

    def update_news(self, news, data):
        """
        Updates the fields of a news instance with the given data.

        Args:
            news: The News instance to be updated.
            data: A dictionary of field-value pairs to update the news instance with.
        """
        for field, value in data.items():
            setattr(news, field, value)
        news.save()

    @extend_schema(
        summary="List News Items",
        description="Retrieves a list of all news items, providing a paginated response. Supports filtering and searching.",
        responses={200: NewsTranslationsSerializer(many=True)},
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
        Retrieves a list of all news items available in the database. This method provides a paginated response
        containing news items serialized using the NewsTranslationsSerializer.

        This method overrides the default list behavior to utilize the custom queryset and serializer class defined
        in the NewsView. It supports filtering, searching, and pagination out of the box as configured in the viewset.

        Args:
            request: HttpRequest object, containing query parameters for filtering and pagination.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HttpResponse with the serialized news data or an error message if no news items are found.
        """
        return super().list(request, *args, **kwargs)

    # Create news
    @extend_schema(
        summary="Create a News Item",
        description="Creates a new news item, optionally including a photo upload. Enforces a limit on the total number of stored news items.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "maxLength": 60},
                    "title_en": {"type": "string", "maxLength": 60},
                    "sub_text": {"type": "string", "maxLength": 175},
                    "sub_text_en": {"type": "string", "maxLength": 175},
                    "url": {"type": "string", "format": "uri"},
                    "photo": {"type": "string", "format": "binary"},
                },
                "required": ["title", "sub_text", "url", "photo"],
            }
        },
        responses={
            201: NewsTranslationsSerializer,
            400: {"description": "Помилка при створені ValidationError"},
            500: {"description": "Помилка сервера"},
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Creates a new news item with optional photo upload. The photo, if provided, is processed and converted
        to webP format using the handle_photo method. This method also enforces a limit on the total number
        of news items stored, deleting the oldest news item if the limit is exceeded.

        This process includes validating the input data with the NewsTranslationsSerializer, handling the photo
        upload, saving the new news item, and optionally performing cleanup operations.

        Args:
            request: HttpRequest object containing the news item's data and an optional 'photo' file in its FILES.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HttpResponse indicating the outcome of the creation operation, either success with the created
            news item's data or failure with an error message.
        """

        try:
            serilaizer = self.get_serializer(
                data=request.data, context={"request": request, "view": self}
            )
            serilaizer.is_valid(raise_exception=True)
            serilaizer.save()

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
        summary="Update a News Item",
        description="Updates an existing news item by ID. Allows for modifying content and replacing the photo.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "maxLength": 60},
                    "title_en": {"type": "string", "maxLength": 60},
                    "sub_text": {"type": "string", "maxLength": 175},
                    "sub_text_en": {"type": "string", "maxLength": 175},
                    "url": {"type": "string", "format": "uri"},
                    "photo": {"type": "string", "format": "binary"},
                },
            }
        },
        responses={
            200: NewsTranslationsSerializer,
            400: {"description": "Помилка при оновлені ValidationError"},
            404: {"description": "Новини не знайдена"},
            500: {"description": "Помилка сервера"},
        },
    )
    def update(self, request, pk, *args, **kwargs):
        """
        Updates an existing news item identified by its primary key (pk). This includes updating textual content
        and optionally replacing the existing photo with a new one. If a new photo is provided, it replaces the
        existing photo after conversion to webP format via the handle_photo method.

        This method ensures that the input data is validated using the NewsTranslationsSerializer and applies the
        updates to the specified news item. If the news item cannot be found, a 404 response is returned.

        Args:
            request: HttpRequest object containing the updated data and an optional 'photo' file.
            pk: Primary key (UUID) of the news item to be updated.

        Returns:
            Response: An HttpResponse indicating the outcome of the update operation, either success with the updated
            news item's data or failure with an appropriate error message.
        """
        try:
            news = News.objects.get(pk=pk)
            serilaizer = self.get_serializer(
                news, data=request.data, context={"request": request, "view": self}
            )
            serilaizer.is_valid(raise_exception=True)
            self.update_news(news, serilaizer.validated_data)
            self.perform_update(serializer=serilaizer)
            return Response(serilaizer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {"description": f"Помилка при оновлені {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except News.DoesNotExist:
            return Response(
                {"message": "Новини не знайдено"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"description": f"Помилка сервера {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Delete a News Item",
        description="Deletes a news item by ID, including any associated photos and their storage.",
        responses={
            200: {"description": "Новина видалена"},
            404: {"description": "Новини не знайдено"},
            500: {"description": "Помилка сервера"},
        },
    )
    def destroy(self, request, pk, *args, **kwargs):
        """
        Deletes a specific news item identified by its primary key (pk). Before deletion, it ensures that any associated
        photo and its file stored in Backblaze storage are also deleted, preventing orphaned files.

        This method handles the deletion process, including looking up the news item, deleting associated resources,
        and then deleting the news item itself. If the specified news item cannot be found, a 404 response is returned.

        Args:
            request: HttpRequest object.
            pk: Primary key (UUID) of the news item to be deleted.

        Returns:
            Response: An HttpResponse indicating the success of the deletion operation or failure with an error message
            if the news item cannot be found or if an internal error occurs.
        """
        try:
            news_item = News.objects.get(pk=pk)
            if news_item.photo:
                delete_file_from_backblaze(news_item.photo_id)
            news_item.photo.delete()
            news_item.delete()

            return Response({"message": "Новина видалена"}, status=status.HTTP_200_OK)

        except News.DoesNotExist:
            return Response(
                {"message": "Новини не знайдено"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Partners-----------------------------------------------------------


class PartnersView(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    ViewSet for managing partner entries in the system. Allows listing all partners, creating new partner entries,
    and deleting existing ones. Partners can have logos, which are converted to webP format upon upload.
    """

    queryset = Partners.objects.all().prefetch_related("logo")
    permission_classes = [IsAuthenticated, IsApprovedUser]
    serializer_class = PartnerSerializer

    def upload_logo(self, *, logo):
        """
        Handles the upload and conversion of a partner's logo to webP format. If a logo is provided,
        it is converted, and a new FileModel instance is created to represent the uploaded and converted logo.

        Args:
            logo: The uploaded logo file.

        Returns:
            FileModel: An instance representing the converted logo's storage details.
        """
        if logo:
            webp_image_name, webp_image_id, image_url = converter_to_webP(logo)
            new_file = FileModel.objects.create(
                id=webp_image_id, name=webp_image_name, url=image_url, category="image"
            )
        return new_file

    @extend_schema(
        summary="List all partners",
        responses={200: PartnerSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """
        Lists all partners currently registered in the system. This method leverages the configured queryset
        and serializer_class to provide a paginated response containing all partners, serialized using the PartnerSerializer.

        Args:
            request: HttpRequest object, potentially containing query parameters for filtering and pagination.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HttpResponse with the serialized list of partners.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new partner",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "logo": {"type": "string", "format": "binary"},
                    "website": {"type": "string", "format": "uri"},
                },
            }
        },
        responses={
            201: PartnerSerializer,
            400: {"description": "Помилка при додаванні ValidationError"},
            500: {"description": "Помилка сервера"},
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Creates a new partner entry in the system. This process may include uploading and converting a logo
        to webP format if a logo file is provided in the request. The new partner, including the converted logo,
        is then saved and returned in the response.

        Args:
            request: HttpRequest object containing the new partner's data and an optional logo file in FILES.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HttpResponse indicating the outcome of the create operation, with the newly created partner's
            data on success or an error message on failure.
        """
        data = {}
        logo = request.FILES.get("logo")
        data["website"] = request.data.get("website")
        try:
            new_file = self.upload_logo(logo=logo)
            if new_file:
                data["name"] = new_file.name
                data["logo"] = new_file
            new_partner = Partners.objects.create(**data)
            serializer = PartnerSerializer(new_partner)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {"description": f"Помилка при додаванні {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Delete a partner",
        responses={
            200: {"description": "Партнер був видалений"},
            404: {"description": "Партнер не знайдено"},
            500: {"description": "Помилка сервера"},
        },
    )
    def destroy(self, request, pk, *args, **kwargs):
        """
        Deletes an existing partner entry identified by the primary key (pk). Before deletion, it ensures that
        any associated logo and its file stored in Backblaze storage are also deleted, preventing orphaned files.

        Args:
            request: HttpRequest object.
            pk: Primary key (UUID or int) of the partner to be deleted.

        Returns:
            Response: An HttpResponse indicating the success of the deletion operation or failure with an error message
            if the partner cannot be found or if an internal error occurs.
        """
        try:
            partner = Partners.objects.get(pk=pk)
            if partner.logo is not None:
                delete_file_from_backblaze(partner.logo_id)
            partner.logo.delete()
            partner.delete()
            return Response(
                {"description": "Партнер був видалений"}, status=status.HTTP_200_OK
            )
        except Partners.DoesNotExist:
            return Response(
                {"description": "Партнер не знайдено"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {"description": "Помилка cервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
