from django.contrib.auth.hashers import check_password
from rest_framework.validators import ValidationError
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserMini
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema
import json
import os
import re

# Create your views here.


class AuthenticationService(ViewSet):
    permission_classes = [AllowAny]

    @staticmethod
    def email_validation(*, email: str):

        if email is None:
            raise ValidationError({'error': 'потрібна електронна пошта'})

        if email == '':
            raise ValidationError(
                {'error': 'Будь ласка, заповніть всі обов\'язкові поля'})

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise ValidationError(
                {'error': 'Невірний формат електронної пошти'})

    @staticmethod
    def password_validation(*, password: str, confirmPassword: str):

        if (password or confirmPassword) == '':
            raise ValidationError(
                {'error': 'Будь ласка, заповніть всі обов\'язкові поля'})

        password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!-_)(.,]).{8,12}$'
        if not re.match(password_regex, password or confirmPassword):
            raise ValidationError(
                {'error': 'Пароль повинен містити великі та малі букви, цифри та один з спеціальних символів, і мати від 8 до 12 символів'})
        if password != confirmPassword:
            raise ValidationError({'error': 'Паролі не співпадають'})

    def get_queryset(self):
        # Return an empty queryset
        return UserMini.objects.none()

    @extend_schema(
        description="Register a new user",
        responses={201: None, 400: 'Registration error'}
    )
    @action(detail=False, methods=['POST'], url_path='register')
    def register(self, request):
        data = json.loads(request.body)
        email = data['email']
        password = data['password']
        confirmPassword = data['confirmPassword']
        first_name = data['first_name']
        last_name = data['last_name']
        # check if the password is valid
        self.email_validation(email=email)
        self.password_validation(
            password=password, confirmPassword=confirmPassword)
    # check if the user is already exist
        user = UserMini.objects.filter(email=email).first()
        if user:
            raise ValidationError(
                {'error': 'Помилка регистрації.'})

    # create a new user
        new_user = UserMini.objects.create(
            first_name=first_name, last_name=last_name,
            email=email, password=make_password(password)
        )
        new_user.save()
        return Response({'message': 'Користувач зареєстрований', 'email': email}, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Log in a user",
        responses={200: None, 400: 'Invalid email or password'}
    )
    @action(detail=False, methods=['POST'], url_path='login')
    def login(self, request):
        data = json.loads(request.body)
        email = data['email']
        password = data['password']

        if not email or not password:
            raise ValidationError(
                {'error': 'Електронна пошта та пароль потрібні'})

        user = UserMini.objects.filter(email=email).first()
        admin = User.objects.filter(email=email).first()

        user_to_authenticate = admin if admin else user
        if not user_to_authenticate:
            raise ValidationError({'error': 'Користувач не знайдений'})

        if not check_password(password, user_to_authenticate.password):
            raise ValidationError({'error': 'Неправильний пароль'})
        
        refresh = RefreshToken.for_user(user_to_authenticate)
        accsess = str(refresh.access_token)

        return Response({'message': 'Користувач увійшов в систему', 'access_token': accsess}, status=status.HTTP_200_OK)

    @extend_schema(
        description="Reset password",
        responses={200: None, 400: 'Invalid token or request'}
    )
    @action(detail=False, methods=['POST'], url_path='reset-password/<uidb64>/<token>')
    def reset_password(self, request, uidb64, token):
        try:
            new_password_data = json.loads(request.body)
            password = new_password_data['password']
            confirmPassword = new_password_data['confirmPassword']
            self.password_validation(
                password=password, confirmPassword=confirmPassword)
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserMini.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response({'message': 'Скидання пароля Успішні'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Неприпустимий токен'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return Response({'error': f'Невірний запит {e}'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Forgot password",
        responses={200: None, 400: 'Email does not exist'}
    )
    @action(detail=False, methods=['POST'], url_path='forgot-password')
    def forgot_password(self, request):
        data = json.loads(request.body)
        email = data['email']
        self.email_validation(email=email)
        try:
            domain = os.environ.get('DOMAIN')
            user = UserMini.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            password_reset_link = f'{domain}/reset-passoword/{uid}/{token}'
            send_mail(
                'Скинути пароль',
                f'Клацніть, щоб посилання на скидання пароля : {password_reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({"message": "Електронна пошта була успішно надіслана"})
        except User.DoesNotExist:
            return Response({"error": "Електронна пошта не існує"}, status=status.HTTP_400_BAD_REQUEST)
