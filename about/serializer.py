from rest_framework.serializers import ModelSerializer
from about.models import AboutModel
from backblaze.serializer import FileSerializer


class AboutSerializer(ModelSerializer):
    images = FileSerializer(many=True)

    class Meta:
        model = AboutModel
        fields = ['quantity_of_animals', 'quantity_of_employees',
                  'quantity_of_succeeds_adoptions', 'images']
