from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from main_page.models import NewsModel as News
from backblaze.utils.b2_utils import converter_to_webP
from backblaze.utils.validation import image_validation
from rest_framework.permissions import IsAuthenticated
from backblaze.models import FileModel
from dog_card.models import DogCardModel
from main_page.serializer import NewsSerializer
from dog_card.serializer import DogCardSerializer
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.cache import cache
# Create your views here.


class main_page_view(APIView):
    permission_classes = [AllowAny]

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
    def get(self, request):
        # Get news from database
        chached_data = cache.get('main_page_data')
        if chached_data:
            return Response(chached_data, status=status.HTTP_200_OK)
        try:
            news = News.objects.all()[:4]
            dog_cards = DogCardModel.objects.all()
            # Serialize news and dog cards
            news_serializer = NewsSerializer(
                news, many=True, context={'request': request})
            dog_card_serializer = DogCardSerializer(dog_cards, many=True)
            response_data = {
                'news_data':  news_serializer.data,
                'dog_cards': dog_card_serializer.data
            }

            cache.set('main_page_data', response_data)
            return Response(response_data, status=status.HTTP_200_OK)

        except News.DoesNotExist:
            # Specific exception handling
            return Response({'message': 'News not found'}, status=status.HTTP_404_NOT_FOUND)
        except DogCardModel.DoesNotExist:
            # Specific exception handling
            return Response({'message': 'Dog cards not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NewsAdminView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
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
    def list(self, request, *args, **kwargs):
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

        image_validation(photo)

        webp_image_name, webp_image_id, bucket_name = converter_to_webP(photo)
        image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
        new_file = FileModel.objects.create(
            id=webp_image_id, name=webp_image_name, url=image_url, category='image')

        new_news = News.objects.create(
            title=title, sub_text=sub_text, url=url, photo=new_file)
        news_serializer = NewsSerializer(new_news, many=True)

        return Response({'massage': 'news was created',
                        'news': {
                            news_serializer.data,
                        }
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        pass

    def delete(self, request, *args, **kwargs):
        pass


# @api_view(['GET'])
# def main_page_view(request):
#     # Get news from database
#     try:
#         news = News.objects.order_by('-post_at')[:4]
#         # Get dog cards from database
#         dog_cards = DogCardModel.objects.all()

#         # Serialize news and dog cards
#         news_serializer = NewsSerializer(news, many=True)
#         dog_card_serializer = DogCardSerializer(dog_cards, many=True)
#         return Response({'news_data': news_serializer.data, 'dog_cards': dog_card_serializer.data}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # Create news


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_news(request):
#     title = request.data['title']
#     sub_text = request.data['sub_text']
#     url = request.data['url']
#     photo = request.FILES['photo']

#     image_validation(photo)

#     webp_image_name, webp_image_id, bucket_name = converter_to_webP(photo)
#     image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
#     new_file = FileModel.objects.create(
#         id=webp_image_id, name=webp_image_name, url=image_url, category='image')
#     new_file.save()

#     new_news = News.objects.create(
#         title=title, sub_text=sub_text, url=url, photo=new_file)
#     new_news.save()
#     return Response({'massage': 'news was created',
#                      'news': {
#                          'id': new_news.id,
#                          'title': new_news.title,
#                          'sub_text': new_news.sub_text,
#                          'url': new_news.url,
#                          'photo': {
#                              'id': new_news.photo.id,
#                              'name': new_news.photo.name,
#                              'url': new_news.photo.url,
#                              'category': new_news.photo.category}
#                      }
#                      }, status=status.HTTP_201_CREATED)
