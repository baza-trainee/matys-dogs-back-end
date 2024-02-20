from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from dog_card.serializer import DogForPick
from .models import CallbackForm
import re


class UserCallBack(ModelSerializer):

    class Meta:
        model = CallbackForm
        fields = ("id", "name", "phone_number", "comment", "id_dog")

    def validate_fields(self, validated_data):

        name = validated_data["name"]
        phone_number = validated_data["phone_number"]
        # Validate minimum length
        if len(name) < 2:
            raise ValidationError("Введіть щонайменше 2 символи")
        # Validate allowed characters (latin, cyrillic, space, dash, apostrophe)
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁіІїЇґҐєЄ\'\-\s]+$", name):
            raise ValidationError(
                "Дозволена латиниця, кирилиця, пробіл, дефіс, апостроф"
            )

        phone_pattern = re.compile(
            r"^(?:\+3\s?8\s?)?(?:\(0\d{2}\)|0\d{2})\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}$"
        )
        if not phone_pattern.match(phone_number):
            raise ValidationError("Введіть коректний номер мобільного")


class Notice(ModelSerializer):
    id_dog = DogForPick()

    class Meta:
        model = CallbackForm
        read_only_fields = ("id", "name", "phone_number", "comment")
        fields = (
            "id",
            "name",
            "phone_number",
            "comment",
            "id_dog",
            "is_read",
            "status",
            "processing",
        )


class NoticeUpdateSerializer(ModelSerializer):

    class Meta:
        model = CallbackForm
        fields = ("id", "is_read", "status", "processing")
