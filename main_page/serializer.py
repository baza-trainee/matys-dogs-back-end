from rest_framework.serializers import ModelSerializer
from main_page.models import NewsModel as News, Partners
from backblaze.serializer import FileSerializer
from rest_framework.exceptions import ValidationError


class NewsSerializer(ModelSerializer):
    photo = FileSerializer()

    class Meta:
        model = News
        fields = ("id", "title", "sub_text", "post_at", "update_at", "url", "photo")


class NewsTranslationsSerializer(ModelSerializer):
    photo = FileSerializer(allow_null=True, required=False)

    class Meta:
        model = News
        fields = (
            "id",
            "title",
            "title_en",
            "sub_text",
            "sub_text_en",
            "post_at",
            "update_at",
            "url",
            "photo",
        )

    def validate_fields(self, validated_data):
        title, title_en = validated_data["title"], validated_data["title_en"]
        sub_text, sub_text_en = (
            validated_data["sub_text"],
            validated_data["sub_text_en"],
        )
        if len(title) > 60 or len(title_en) > 60:
            raise ValidationError("Довжина поля title повинна бути менше 60 символів")
        if len(sub_text) > 150 or len(sub_text_en) > 150:
            raise ValidationError(
                "Довжина поля sub_text повинна бути менше 150 символів"
            )

    def create(self, validated_data):
        photo_data = self.context["request"].FILES.get("photo", None)
        if photo_data is not None:
            photo_obj = self.context["view"].handle_photo(photo_data, None)
            validated_data["photo"] = photo_obj
            news = News.objects.create(**validated_data)
        return news

    def update(self, instance, validated_data):
        photo_data = self.context["request"].FILES.get("photo", None)
        if photo_data is not None:
            photo_obj = self.context["view"].handle_photo(photo_data, instance)
            validated_data["photo"] = photo_obj
        news = super().update(instance, validated_data)
        return news


class PartnerSerializer(ModelSerializer):
    logo = FileSerializer()

    class Meta:
        model = Partners
        fields = ("id", "name", "logo", "website")
