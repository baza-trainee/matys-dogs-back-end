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
        comment = validated_data["comment"]
        if len(name) < 2:
            raise ValidationError("Введіть щонайменше 2 символи")
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁіІїЇґҐєЄ\'`’ʼ\-\s]+$", name):
            raise ValidationError(
                "Дозволена латиниця, кирилиця, пробіл, дефіс, апостроф"
            )
        phone_pattern = re.compile(
            r"^(?:\+3\s?8\s?)?(?:\(0\d{2}\)|0\d{2})\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}$"
        )
        if not phone_pattern.match(phone_number):
            raise ValidationError("Введіть коректний номер мобільного")
        if len(comment) > 300:
            raise ValidationError("Коментар занадто довгий")


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
            "date",
            "is_read",
            "status",
            "processing",
        )


class NoticeUpdateSerializer(ModelSerializer):

    class Meta:
        model = CallbackForm
        fields = ("id", "is_read", "status", "processing")
