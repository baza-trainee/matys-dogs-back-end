from rest_framework.serializers import ModelSerializer
from dog_card.models import DogCardModel
from backblaze.serializer import FileSerializer


# Serializers define the API representation.


class DogCardSerializer(ModelSerializer):
    photo = FileSerializer()

    class Meta:
        model = DogCardModel
        fields = ['id', 'name', 'ready_for_adoption',
                  'gender', 'age', 'sterilization', 'vaccination_parasite_treatment', 'size', 'description', 'photo']

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = super().to_representation(instance)

        if 'request' in self.context:
            language = self.context['request'].headers.get(
                'Accept-Language', '').lower()

            ret['name'] = instance.name_en if language == 'en' else instance.name_uk
            ret['description'] = instance.description_en if language == 'en' else instance.description_uk
            ret['gender'] = instance.gender_en if language == 'en' else instance.gender_uk
            ret['size'] = instance.size_en if language == 'en' else instance.size_uk
            ret['age'] = instance.age_en if language == 'en' else instance.age_uk

            ret.pop('name_en', None)
            ret.pop('name_uk', None)
            ret.pop('description_en', None)
            ret.pop('description_uk', None)
            ret.pop('gender_en', None)
            ret.pop('gender_uk', None)
            ret.pop('size_en', None)
            ret.pop('size_uk', None)
            ret.pop('age_en', None)
            ret.pop('age_uk', None)

        return ret
