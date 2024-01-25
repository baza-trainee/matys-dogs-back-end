from rest_framework.serializers import ModelSerializer
from main_page.models import NewsModel as News, Partners
from backblaze.serializer import FileSerializer


# Serializers define the API representation.


class NewsSerializer(ModelSerializer):
    photo = FileSerializer()

    class Meta:
        model = News
        fields = ('id', 'title', 'sub_text', 'post_at',
                  'update_at', 'url', 'photo')


class PartnerSerializer(ModelSerializer):
    logo = FileSerializer()

    class Meta:
        model = Partners
        fields = ('id', 'name', 'logo')
