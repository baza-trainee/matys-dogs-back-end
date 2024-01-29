from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from main_page.models import NewsModel as News, Partners
from backblaze.utils.b2_utils import converter_to_webP, delete_file_from_backblaze
from backblaze.utils.validation import image_validation
from rest_framework.permissions import IsAuthenticated
from backblaze.models import FileModel
from dog_card.models import DogCardModel
from main_page.serializer import NewsSerializer, PartnerSerializer
from dog_card.serializer import DogCardSerializer
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from api.models import IsApprovedUser
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)
# Main Page -------------------------------------------------------------------


class main_page_view(mixins.ListModelMixin, GenericViewSet):
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
    serializer_mapping = {
        News: NewsSerializer,
        Partners: PartnerSerializer,
        DogCardModel: DogCardSerializer
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
        ]
    )
    def list(self, request):
        """
        This method is called when a GET request is made to the view. It retrieves the necessary data from the database, serializes it using the appropriate serializers, and returns the serialized data as a response.

        Parameters:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object containing the serialized data.

        Raises:
            Http404: If no data is found, a 404 Not Found response is raised.
        """
        news_queryset = News.objects.all()[:4]
        dog_cards_queryset = DogCardModel.objects.all()
        partners_queryset = Partners.objects.all()

        # Serialize news and dog cards
        news_serializer = self.serializer_mapping[News](
            news_queryset, many=True)
        dog_cards_serializer = self.serializer_mapping[DogCardModel](
            dog_cards_queryset, many=True)
        partners_serializer = self.serializer_mapping[Partners](
            partners_queryset, many=True)

        # Make response data
        response_data = {
            'news': news_serializer.data,
            'partners': partners_serializer.data,
            'dog_cards': dog_cards_serializer.data
        }
        if not response_data['news'] and not response_data['dog_cards'] and not response_data['partners']:
            raise Http404("No data found")
        return Response(response_data, status=status.HTTP_200_OK)

# News------------------------------------------------------------------


class NewsView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated, IsApprovedUser]
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def upload_photo(self, *, photo):
        """
        This method uploads a photo to the backblaze
        """
        if photo:
            image_validation(photo)
            webp_image_name, webp_image_id, bucket_name, _ = converter_to_webP(
                photo)
            image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
            new_file = FileModel.objects.create(
                id=webp_image_id, name=webp_image_name, url=image_url, category='image')
        return new_file

    def update_photo(self, *, photo, cur_news):
        """
        This method updates a photo to the backblaze
        """
        if photo:
            delete_file_from_backblaze(cur_news.photo_id)
            cur_news.photo.delete()
            image_validation(photo)
            webp_image_name, webp_image_id, bucket_name, _ = converter_to_webP(
                photo)
            image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
            new_file = FileModel.objects.create(
                id=webp_image_id, name=webp_image_name, url=image_url, category='image')
        return new_file

    @extend_schema(
        summary='List News Items',
        description='Retrieves a list of all news items.',
        responses={
            200: NewsSerializer(many=True),
            404: {'description': 'News not found'}
        }
    )
    def list(self, request):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'message': 'Новини не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"news": serializer.data})

    # Create news
    @extend_schema(
        summary='Create a News Item',
        description='Creates a new news item with the given details.',
        request=NewsSerializer,
        responses={
            201: NewsSerializer,
            400: {'description': 'Invalid data'}
        }
    )
    def create(self, request, *args, **kwargs):
        title = request.data.get('title')
        sub_text = request.data.get('sub_text')
        url = request.data.get('url')
        photo = request.FILES.get('photo')

        new_file = self.upload_photo(photo=photo)
        new_news = News.objects.create(
            title=title, sub_text=sub_text, url=url, photo=new_file)
        news_serializer = NewsSerializer(new_news)

        if News.objects.count() > 5:
            old_news = News.objects.last()
            delete_file_from_backblaze(old_news.photo_id)
            old_news.photo.delete()
            old_news.delete()

        return Response({'massage': 'news was created', 'news': news_serializer.data
                         }, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary='Update a News Item',
        description='Updates the news item with the given details.',
        request=NewsSerializer,
        responses={
            200: NewsSerializer,
            404: {'description': 'News not found'},
            500: {'description': 'Internal server error'}
        }
    )
    def update(self, request, pk):
        """
        Updates a news item identified by the primary key (pk).
        """
        title = request.data.get('title')
        sub_text = request.data.get('sub_text')
        url = request.data.get('url')
        photo = request.FILES.get('photo')
        try:
            news = News.objects.get(pk=pk)
            new_file = self.update_photo(photo=photo, cur_news=news)
            if new_file:
                news.photo = new_file
            news.title = title
            news.sub_text = sub_text
            news.url = url
            news.save()
            return Response({'message': 'Новини були оновлені'}, status=status.HTTP_200_OK)
        except News.DoesNotExist:
            return Response({'message': 'Новини не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary='Delete a News Item',
        description='Deletes the news item with the specified ID.',
        responses={
            status.HTTP_200_OK: {'description': 'Новини успішно видалили'},
            status.HTTP_404_NOT_FOUND: {'description': 'Новини не знайдено'},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                'description': 'Внутрішня помилка сервера'}
        }
    )
    def destroy(self, request, pk):
        """
        Deletes a news item identified by the primary key (pk).
        """
        try:
            news_item = News.objects.get(pk=pk)
            delete_file_from_backblaze(news_item.photo_id)
            news_item.photo.delete()
            news_item.delete()

            return Response({'message': 'Новини були видалені'}, status=status.HTTP_200_OK)

        except News.DoesNotExist:
            return Response({'message': 'Новини не знайдено'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f'Помилка видалення новин: {e}', exc_info=True)
            return Response({'message': 'Внутрішня помилка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Partners-----------------------------------------------------------


class PartnersView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = Partners.objects.all()
    permission_classes = [IsAuthenticated, IsApprovedUser]
    serializer_class = PartnerSerializer

    def upload_logo(self, *, logo):
        if logo:
            image_validation(logo)
            webp_image_name, webp_image_id, bucket_name, _ = converter_to_webP(
                logo)
            image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
            new_file = FileModel.objects.create(
                id=webp_image_id, name=webp_image_name, url=image_url, category='image')
        return new_file

    @extend_schema(
        summary='List all partners',
        responses={
            200: PartnerSerializer(many=True),
            404: {'description': 'Партнери не знайдені'},
            500: {'description': 'Внутрішня помилка сервера'}
        }
    )
    def list(self, request):
        try:
            partners = Partners.objects.all()
            partners_serializer = PartnerSerializer(partners, many=True)

            return Response(partners_serializer.data, status=status.HTTP_200_OK)
        except Partners.DoesNotExist:
            return Response({'message': 'Partners not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary='Create a new partner',
        request=PartnerSerializer,
        responses={
            201: PartnerSerializer,
            400: {'description': 'Поганий запит - недійсні дані'},
            500: {'description': 'Внутрішня помилка сервера'}
        }
    )
    def create(self, request, *args, **kwargs):
        logo = request.FILES.get('logo')
        data = {}
        try:
            new_file = self.upload_logo(logo=logo)
            if new_file:
                data['name'] = new_file.name
                data['logo'] = new_file
            new_partner = Partners.objects.create(**data)
            serializer = PartnerSerializer(new_partner)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary='Delete a partner',
        responses={
            200: {'description': 'Партнер був видалений'},
            404: {'description': 'Партнер не знайдено'},
            500: {'description': 'Внутрішня помилка сервера'}
        }
    )
    def destroy(self, request, pk):
        try:
            partner = Partners.objects.get(pk=pk)
            delete_file_from_backblaze(partner.logo_id)
            partner.logo.delete()
            partner.delete()
            return Response({'message': 'Партнер був видалений'}, status=status.HTTP_200_OK)
        except Partners.DoesNotExist:
            return Response({'message': 'Партнер не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
