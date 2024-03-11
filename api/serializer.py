from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import UserMini


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class UserMiniSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserMini
        fields = ('id', 'is_approved', 'user')


class UserToApprove(ModelSerializer):

    class Meta:
        model = UserMini
        fields = ('id', 'is_approved')
