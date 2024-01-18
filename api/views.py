from django.contrib.auth.hashers import check_password
from rest_framework.validators import ValidationError
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.models import User
from api.validation import email_validation, password_validation
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import json
import os
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
    return Response({'message': 'Користувач зареєстрований', 'email': data['email']}, status=status.HTTP_201_CREATED)


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
    return Response({'message': 'Користувач увійшов в систему', 'access_token': accsess, }, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request, uidb64, token):
    try:
        new_password_data = json.loads(request.body)
        password_validation(
            new_password_data['password'], new_password_data['confirmPassword'])

        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password_data['password'])
            user.save()
            return Response({'message': 'Скидання пароля Успішні'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Неприпустимий токен'}, status=status.HTTP_400_BAD_REQUEST)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'error': 'Невірний запит'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def forgot_password(request):
    data = json.loads(request.body)
    try:
        domain = os.environ.get('DOMAIN')
        user = User.objects.get(email=data['email'])
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        password_reset_link = f'{domain}/reset-passoword/{uid}/{token}'
        send_mail(
            'Скинути пароль',
            f'Клацніть, щоб посилання на скидання пароля : {password_reset_link}',
            settings.EMAIL_HOST_USER,
            [data['email']],
            fail_silently=False,
        )
        return Response({"message": "Електронна пошта була успішно надіслана"})
    except User.DoesNotExist:
        return Response({"error": "Електронна пошта не існує"}, status=status.HTTP_400_BAD_REQUEST)
