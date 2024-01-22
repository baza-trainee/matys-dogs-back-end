from rest_framework.serializers import ModelSerializer
from main_page.models import NewsModel as News, Partners
from backblaze.serializer import FileSerializer


class NewsSerializer(ModelSerializer):
    photo = FileSerializer()

    class Meta:
        model = News
        fields = ['id', 'title_uk', 'title_en', 'post_at',
                  'update_at', 'sub_text_uk', 'sub_text_en', 'url', 'photo']

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = super().to_representation(instance)

        # Check if the request is part of the serializer context
        if 'request' in self.context:

            language = self.context.get('language')
            if not language:
                language = self.context['request'].headers.get(
                    'Accept-Language', '').lower()

            # Assign the language-specific fields to the main dictionary
            ret['title'] = instance.title_en if language == 'en' else instance.title_uk
            ret['sub_text'] = instance.sub_text_en if language == 'en' else instance.sub_text_uk

            # Remove the language-specific fields from the representation
            for field in ['title_uk', 'title_en', 'sub_text_uk', 'sub_text_en']:
                ret.pop(field, None)

        return ret


class PartnerSerializer(ModelSerializer):
    logo = FileSerializer()

    class Meta:
        model = Partners
        fields = ['id', 'name', 'logo']
