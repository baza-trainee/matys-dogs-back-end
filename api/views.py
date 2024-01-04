from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.models import User
from api.validation import email_validation, password_validation
from rest_framework_simplejwt.tokens import RefreshToken
import json

# Create your views here.


@api_view(['POST'])
@csrf_exempt
def register(request):
    # get the data from the request
    data = json.loads(request.body)
    # check if the password is valid
    email_validation(data['email'])
    password_validation(data['password'], data['confirmPassword'])
    # check if the user is already exist
    user = User.objects.filter(email=data['email']).first()
    if user:
        return Response({'error': 'Помилка регистрації.'}, status=status.HTTP_400_BAD_REQUEST)
    # create a new user
    new_user = User.objects.create_user(
        username='admin',
        email=data['email'], password=data['password'])
    new_user.save()
    return Response({'massage': 'Користувач зареєстрований', 'email': data['email']}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@csrf_exempt
def login(request):
    # get the data from the request
    data = json.loads(request.body)
    # check if the data is valid
    email_validation(data['email'])
    # check if the user is exist
    user = User.objects.filter(email=data['email']).first()
    if not user:
        raise ValidationError({'error': 'Пошта або пароль не існують'})
    # check if the password is correct
    if not check_password(data['password'], user.password):
        raise ValidationError({'error': 'Неправильний пароль'})
    # create a refresh token
    refesh = RefreshToken.for_user(user)
    # create a access token
    accsess = str(refesh.access_token)
    return Response({'message': 'Користувач увійшов в систему', 'accsess': accsess, }, status=status.HTTP_200_OK)
