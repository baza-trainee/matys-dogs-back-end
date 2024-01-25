from rest_framework.response import Response
from rest_framework import status
from main_page.models import NewsModel as News, Partners
from backblaze.utils.b2_utils import converter_to_webP
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

# Create your views here.


class main_page_view(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    queryset = News.objects.all()
    serializer_class = NewsSerializer

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
        try:
            news_queryset = News.objects.all()[:4]
            dog_cards_queryset = DogCardModel.objects.all()
            partners_queryset = Partners.objects.all()

            news_serializer = NewsSerializer(news_queryset, many=True)
            dog_cards_serializer = DogCardSerializer(
                dog_cards_queryset, many=True)
            partners_serializer = PartnerSerializer(
                partners_queryset, many=True)

            # Serialize news and dog cards
            response_data = {
                'news': news_serializer.data,
                'partners': partners_serializer.data,
                'dog_cards': dog_cards_serializer.data
            }
            # cache.set('main_page_data', response_data)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# News


class NewsView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    @extend_schema(
        summary='List News Items',
        description='Retrieves a list of all news items.',
        responses={
            200: NewsSerializer(many=True),
            404: {'description': 'News not found'}
        }
    )
    def list(self, request):
        queryset = super().get_queryset()
        serializer = NewsSerializer(queryset, many=True)
        if not queryset:
            return Response({'message': 'News not found'}, status=status.HTTP_404_NOT_FOUND)
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
        title = request.data['title']
        sub_text = request.data['sub_text']
        url = request.data['url']
        photo = request.FILES['photo']

        if photo:
            image_validation(photo)
            webp_image_name, webp_image_id, bucket_name, _ = converter_to_webP(
                photo)
            image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
            new_file = FileModel.objects.create(
                id=webp_image_id, name=webp_image_name, url=image_url, category='image')
        new_news = News.objects.create(
            title=title, sub_text=sub_text, url=url, photo=new_file)
        news_serializer = NewsSerializer(new_news)

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
        title = request.data['title']
        sub_text = request.data['sub_text']
        url = request.data['url']
        photo = request.FILES['photo']
        try:
            news = News.objects.get(pk=pk)
            if photo:
                news.photo.delete()
                image_validation(photo)
                webp_image_name, webp_image_id, bucket_name, _ = converter_to_webP(
                    photo)
                image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
                new_file = FileModel.objects.create(
                    id=webp_image_id, name=webp_image_name, url=image_url, category='image')
                news.photo = new_file
            news.title = title
            news.sub_text = sub_text
            news.url = url
            news.save()
            return Response({'message': 'News was updated'}, status=status.HTTP_200_OK)
        except News.DoesNotExist:
            return Response({'message': 'News not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary='Delete a News Item',
        description='Deletes the news item with the specified ID.',
        responses={
            200: {'description': 'Новини були видалені'},
            404: {'description': 'Новини не знайдено'},
            500: {'description': 'Внутрішня помилка сервера'}
        }
    )
    def destroy(self, request, pk):
        try:
            news = News.objects.get(pk=pk)
            file = FileModel.objects.get(pk=news.photo.id)
            file.delete()
            news.delete()
            return Response({'message': 'Новини були видалені'}, status=status.HTTP_200_OK)
        except not news:
            return Response({'message': 'Новини не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Partners
class PartnersView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = Partners.objects.all()
    serializer_class = PartnerSerializer

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
            if logo:
                image_validation(logo)
                webp_image_name, webp_image_id, bucket_name, _ = converter_to_webP(
                    logo)
                image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
                new_file = FileModel.objects.create(
                    id=webp_image_id, name=webp_image_name, url=image_url, category='image')
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
            file = FileModel.objects.get(id=partner.logo.id)
            file.delete()
            partner.delete()
            return Response({'message': 'Партнер був видалений'}, status=status.HTTP_200_OK)
        except Partners.DoesNotExist:
            return Response({'message': 'Партнер не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
