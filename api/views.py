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
from drf_spectacular.utils import extend_schema
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import OpenApiResponse
from rest_framework import viewsets
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
        return User.objects.none()

    @extend_schema(
        summary='Register user',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'User email'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'User password'
                    },
                    'confirmPassword': {
                        'type': 'string',
                        'description': 'Confirmation of user password'
                    },
                    'first_name': {
                        'type': 'string',
                        'description': 'User first name'
                    },
                    'last_name': {
                        'type': 'string',
                        'description': 'User last name'
                    }
                },
                'required': ['email', 'password', 'confirmPassword', 'first_name', 'last_name']
            }
        },
        responses={
            201: OpenApiResponse(
                description='User registration successful',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'Користувач зареєстрований'
                        },
                        'email': {
                            'type': 'string',
                            'example': 'user@example.com'
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description='Invalid request or user already exists',
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string'
                        }
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['POST'], url_path='register')
    def register(self, request):
        data = json.loads(request.body)

        # check if the password is valid
        self.email_validation(email=data['email'])
        self.password_validation(
            password=data['password'], confirmPassword=data['confirmPassword'])

    # check if the user is already exist
        if User.objects.filter(email=data['email']).exists():
            raise ValidationError(
                {'error': 'Помилка регистрації. Користувач вже існує.'})

    # create a new user
        user = User.objects.create(username=data['email'],
                                   first_name=data['first_name'], last_name=data['last_name'],
                                   email=data['email'], password=make_password(
                                       data['password'])
                                   )
        UserMini.objects.create(user=user)
        return Response({'message': 'Користувач зареєстрований', 'email': data['email']}, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary='Login user',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'User email'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'User password'
                    }
                },
                'required': ['email', 'password']
            }
        },
        responses={
            200: OpenApiResponse(
                description='User login successful',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'Користувач увійшов в систему'
                        },
                        'access_token': {
                            'type': 'string',
                            'example': 'access_token_example'
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description='Invalid login credentials',
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string'
                        }
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['POST'], url_path='login')
    def login(self, request):
        data = json.loads(request.body)
        email = data['email']
        password = data['password']

        if not email or not password:
            raise ValidationError(
                {'error': 'Електронна пошта та пароль потрібні'})

        user = User.objects.filter(email=email).first()

        if not user:
            raise ValidationError({'error': 'Користувач не знайдений'})

        if not check_password(password, user.password):
            raise ValidationError({'error': 'Неправильний пароль'})

        refresh = RefreshToken.for_user(user)
        accsess = str(refresh.access_token)

        return Response({'message': 'Користувач увійшов в систему', 'access_token': accsess}, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Reset password',
        parameters=[
            {
                'name': 'uidb64',
                'in': 'path',
                'description': 'Base64 encoded user ID',
                'required': True,
                'schema': {'type': 'string'}
            },
            {
                'name': 'token',
                'in': 'path',
                'description': 'Password reset token',
                'required': True,
                'schema': {'type': 'string'}
            }
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'password': {
                        'type': 'string',
                        'description': 'New password'
                    },
                    'confirmPassword': {
                        'type': 'string',
                        'description': 'Confirm new password'
                    }
                },
                'required': ['password', 'confirmPassword']
            }
        },
        responses={
            200: OpenApiResponse(
                description='Password reset successful',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'Скидання пароля Успішні'
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description='Invalid request or token',
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Неприпустимий токен'
                        }
                    }
                }
            )
        }
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
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response({'message': 'Скидання пароля Успішні'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Неприпустимий токен'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return Response({'error': f'Невірний запит {e}'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary='Forgot password',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'User email for password reset request'
                    }
                },
                'required': ['email']
            }
        },
        responses={
            200: OpenApiResponse(
                description='Password reset email sent successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'Електронна пошта була успішно надіслана'
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description='Invalid request',
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Електронна пошта не існує'
                        }
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['POST'], url_path='forgot-password')
    def forgot_password(self, request):
        data = json.loads(request.body)
        email = data['email']
        self.email_validation(email=email)
        try:
            domain = os.environ.get('DOMAIN')
            user = User.objects.get(email=email)
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserMini.objects.all()
    pass
