from rest_framework.serializers import ModelSerializer
from about.models import AboutModel
from backblaze.serializer import FileSerializer


class AboutSerializer(ModelSerializer):
    images = FileSerializer(many=True)

    class Meta:
        model = AboutModel
        fields = [
            "quantity_of_animals",
            "quantity_of_employees",
            "quantity_of_succeeds_adoptions",
            "images",
        ]


class ImagesSerializer(ModelSerializer):
    images = FileSerializer(many=True)

    class Meta:
        model = AboutModel
        fields = ["images"]
        verbose_name = "Про нас - фото"


class EmploymentSerializer(ModelSerializer):
    class Meta:
        model = AboutModel
        fields = [
            "quantity_of_employees",
            "quantity_of_succeeds_adoptions",
            "quantity_of_animals",
        ]
        verbose_name = "Про нас - статистика"
        extra_kwargs = {
            "quantity_of_employees": {"required": False},
            "quantity_of_succeeds_adoptions": {"required": False},
            "quantity_of_animals": {"required": False},
        }
