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

            for field in ['name_en', 'name_uk', 'description_en', 'description_uk', 'gender_en', 'gender_uk', 'size_en', 'size_uk', 'age_en']:
                ret.pop(field, None)

        return ret
