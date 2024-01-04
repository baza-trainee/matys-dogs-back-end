from rest_framework.response import Response
from rest_framework import status
from main_page.models import NewsModel as News
from rest_framework.decorators import api_view, permission_classes
from backblaze.utils.b2_utils import converter_to_webP
from backblaze.utils.validation import image_validation
from rest_framework.permissions import IsAuthenticated
from backblaze.models import FileModel
from main_page.serializer import NewsSerializer
# Create your views here.


@api_view(['GET'])
def get_news(request):
    getAllNews = News.objects.all()
    serializer = NewsSerializer(getAllNews, many=True)
    return Response({'news': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_news(request):
    title = request.data['title']
    sub_text = request.data['sub_text']
    Text = request.data['Text']
    photo = request.FILES['photo']

    image_validation(photo)

    webp_image_name, webp_image_id, bucket_name = converter_to_webP(photo)
    image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
    new_file = FileModel.objects.create(
        id=webp_image_id, name=webp_image_name, url=image_url, category='image')
    new_file.save()

    new_news = News.objects.create(
        title=title, sub_text=sub_text, Text=Text, photo=new_file)
    new_news.save()
    return Response({'massage': 'news was created',
                     'news': {
                         'id': new_news.id,
                         'title': new_news.title,
                         'sub_text': new_news.sub_text,
                         'Text': new_news.Text,
                         'photo': {
                             'id': new_news.photo.id,
                             'name': new_news.photo.name,
                             'url': new_news.photo.url,
                             'category': new_news.photo.category}
                     }
                     }, status=status.HTTP_201_CREATED)
