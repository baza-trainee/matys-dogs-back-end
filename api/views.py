from django.contrib.auth.hashers import check_password
from rest_framework.validators import ValidationError
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from api.validation import email_validation, password_validation
from rest_framework_simplejwt.tokens import RefreshToken
import json

# Create your views here.


@api_view(['POST'])
def register(request):
    # get the data from the request
    data = json.loads(request.body)
    # check if the password is valid
    email_validation(data['email'])
    password_validation(data['password'], data['confirmPassword'])
    # check if the user is already exist
    user = User.objects.filter(email=data['email']).first()
    if user:
        raise ValidationError(
            {'error': 'Помилка регистрації.'}, status=status.HTTP_400_BAD_REQUEST)
    # create a new user
    new_user = User.objects.create_user(
        username='admin',
        email=data['email'], password=data['password'])
    new_user.save()
    return Response({'massage': 'Користувач зареєстрований', 'email': data['email']}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
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
    return Response({'message': 'Користувач увійшов в систему', 'token_accsess': accsess, }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password(request):
    user_token = request.headers.get('Authorization')
    token_data = user_token.split(' ')[1]
    try:
        user_token = Token.objects.get(key=token_data)
    except not Token:
        return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'message': 'Password reset'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def forgot_password(request):
    email = 'jabsoluty@gmail.com'

    send_mail(
        'Reset passowrd',
        f'Click to link to reset password',
        'matys1dogshelper.gmail.com',
        [email],
        fail_silently=False,
    )
    return Response({"massage": "email was sened succesuly"})
