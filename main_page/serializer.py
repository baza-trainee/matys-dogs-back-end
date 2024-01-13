from rest_framework.serializers import ModelSerializer
from main_page.models import NewsModel as News
from backblaze.serializer import FileSerializer


class NewsSerializer(ModelSerializer):
    photo = FileSerializer()

    class Meta:
        model = News
        fields = ['id', 'title', 'post_at',
                  'update_at', 'sub_text', 'url', 'photo']
