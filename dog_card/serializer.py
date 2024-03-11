from rest_framework.serializers import ModelSerializer
from dog_card.models import DogCardModel
from backblaze.serializer import FileSerializer
from backblaze.utils.b2_utils import delete_file_from_backblaze

# Serializers define the API representation.


class DogCardSerializer(ModelSerializer):
    photo = FileSerializer()

    class Meta:
        model = DogCardModel
        fields = (
            "id",
            "name",
            "ready_for_adoption",
            "gender",
            "age",
            "sterilization",
            "vaccination_parasite_treatment",
            "size",
            "description",
            "photo",
        )


class DogCardTranslationSerializer(ModelSerializer):
    photo = FileSerializer(allow_null=True, required=False)

    class Meta:
        model = DogCardModel
        fields = (
            "id",
            "name",
            "name_en",
            "ready_for_adoption",
            "gender",
            "gender_en",
            "age",
            "age_en",
            "sterilization",
            "vaccination_parasite_treatment",
            "size",
            "size_en",
            "description",
            "description_en",
            "photo",
        )
        extra_kwargs = {
            "sterilization": {"required": False},
            "vaccination_parasite_treatment": {"required": False},
        }

    def create(self, validated_data):
        photo_data = self.context["request"].FILES.get("photo", None)
        if photo_data is not None:
            photo_obj = self.context["view"].handle_photo(photo_data, None)
            validated_data["photo"] = photo_obj
            dog_card = DogCardModel.objects.create(**validated_data)
        return dog_card

    def update(self, instance, validated_data):
        photo_data = self.context["request"].FILES.get("photo", None)
        if photo_data is not None:
            photo_obj = self.context["view"].handle_photo(photo_data, instance)
            validated_data["photo"] = photo_obj
        dog_card = super().update(instance, validated_data)
        return dog_card

    def destroy(self, instance, *args, **kwargs):
        if self.photo:
            delete_file_from_backblaze(self.photo_id)
        super().delete(*args, **kwargs)


class DogForPick(ModelSerializer):

    class Meta:
        model = DogCardModel
        fields = (
            "id",
            "name",
        )
