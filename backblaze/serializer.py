from rest_framework.serializers import ModelSerializer
from backblaze.models import FileModel


class FileSerializer(ModelSerializer):
    class Meta:
        model = FileModel
        fields = ('id', 'name', 'url', 'category')
