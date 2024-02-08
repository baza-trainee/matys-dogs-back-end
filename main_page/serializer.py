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


class NewsTranslationsSerializer(ModelSerializer):
    photo = FileSerializer(allow_null=True, required=False)

    class Meta:
        model = News
        fields = ('id',
                  'title',
                  'title_en',
                  'sub_text',
                  'sub_text_en',
                  'post_at',
                  'update_at',
                  'url',
                  'photo')

    def create(self, validated_data):
        photo_data = self.context['request'].FILES.get('photo', None)
        news = News.objects.create(**validated_data)
        if photo_data:
            photo_obj = self.context['view'].handle_photo(
                photo_data, None)
            if photo_obj:
                news.photo = photo_obj
                news.save()
        return news

    def update(self, instance, validated_data):
        photo_data = self.context['request'].FILES.get('photo', None)
        news = super().update(instance, validated_data)
        if photo_data:
            photo_obj = self.context['view'].handle_photo(
                photo_data, news)
            if photo_obj:
                news.photo = photo_obj
                news.save()
            return news


# Serializers define the API representation.


class PartnerSerializer(ModelSerializer):
    logo = FileSerializer()

    class Meta:
        model = Partners
        fields = ('id', 'name', 'logo')
