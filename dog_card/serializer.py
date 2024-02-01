from rest_framework.serializers import ModelSerializer
from dog_card.models import DogCardModel
from backblaze.serializer import FileSerializer


# Serializers define the API representation.


class DogCardSerializer(ModelSerializer):
    photo = FileSerializer()

    class Meta:
        model = DogCardModel
        fields = ('id', 'name', 'ready_for_adoption',
                  'gender', 'age', 'sterilization', 'vaccination_parasite_treatment', 'size', 'description', 'photo')


class DogCardCreateSerializer(ModelSerializer):
    photo = FileSerializer()

    class Meta:
        model = DogCardModel
        fields = (
            'name',
            'name_en',
            'ready_for_adoption',
            'gender',
            'gender_en',
            'age',
            'age_en',
            'sterilization',
            'vaccination_parasite_treatment',
            'size',
            'size_en',
            'description',
            'description_en',
            'photo'
        )
