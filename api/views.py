from django.contrib.auth.hashers import check_password
from rest_framework.validators import ValidationError
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework.response import Response
from rest_framework import status, mixins
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserMini
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.viewsets import GenericViewSet
from .serializer import UserMiniSerializer, UserToApprove
import json
import os
import re

# Create your views here.


class AuthenticationService(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    permission_classes = [AllowAny]
    serializer_class = UserMiniSerializer

    @staticmethod
    def email_validation(*, email: str):

        if email is None:
            raise ValidationError({"error": "потрібна електронна пошта"})

        if email == "":
            raise ValidationError(
                {"error": "Будь ласка, заповніть всі обов'язкові поля"}
            )

        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            raise ValidationError({"error": "Невірний формат електронної пошти"})

    @staticmethod
    def password_validation(*, password: str, confirmPassword: str):

        if (password or confirmPassword) == "":
            raise ValidationError(
                {"description": "Будь ласка, заповніть всі обов'язкові поля"}
            )

        password_regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!-_)(.,]).{8,12}$"
        if not re.match(password_regex, password or confirmPassword):
            raise ValidationError(
                {
                    "description": "Пароль повинен містити великі та малі букви, цифри та один з спеціальних символів, і мати від 8 до 12 символів"
                }
            )
        if password != confirmPassword:
            raise ValidationError({"description": "Паролі не співпадають"})

    @extend_schema(
        summary="Register user",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "User email",
                    },
                    "password": {"type": "string", "description": "User password"},
                    "confirmPassword": {
                        "type": "string",
                        "description": "Confirmation of user password",
                    },
                    "first_name": {"type": "string", "description": "User first name"},
                    "last_name": {"type": "string", "description": "User last name"},
                },
                "required": [
                    "email",
                    "password",
                    "confirmPassword",
                    "first_name",
                    "last_name",
                ],
            }
        },
        tags=["Authentication"],
        responses={
            201: OpenApiResponse(
                description="User registration successful",
                response={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "example": "Користувач зареєстрований",
                        },
                        "email": {"type": "string", "example": "user@example.com"},
                    },
                },
            ),
            400: {"description": "Помилка при реєстрації ValidationError"},
            500: {"description": "Помилка сервера"},
        },
    )
    @action(detail=False, methods=["POST"], url_path="register")
    def register(self, request):
        try:
            data = json.loads(request.body)

            self.email_validation(email=data["email"])
            self.password_validation(
                password=data["password"], confirmPassword=data["confirmPassword"]
            )

            if User.objects.filter(email=data["email"]).exists():
                raise ValidationError(
                    {"description": "Помилка регистрації. Користувач вже існує."}
                )

            user = User.objects.create(
                username=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                password=make_password(data["password"]),
            )
            UserMini.objects.create(user=user)
            return Response(
                {"description": "Користувач зареєстрований", "email": data["email"]},
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                {"description": f"Помилка при реєстрації {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"description": f"Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Login user",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "User email",
                    },
                    "password": {"type": "string", "description": "User password"},
                },
                "required": ["email", "password"],
            }
        },
        tags=["Authentication"],
        responses={
            200: OpenApiResponse(
                description="User login successful",
                response={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "example": "Користувач увійшов в систему",
                        },
                        "access_token": {
                            "type": "string",
                            "example": "access_token_example",
                        },
                    },
                },
            ),
            400: {"description": "Помилка при вході в систему ValidationError"},
            500: {"description": "Помилка сервера"},
        },
    )
    @action(detail=False, methods=["POST"], url_path="login")
    def login(self, request):
        try:
            data = json.loads(request.body)
            email = data["email"]
            password = data["password"]

            if not email or not password:
                raise ValidationError({"error": "Електронна пошта та пароль потрібні"})

            user = User.objects.filter(email=email).first()

            if not user:
                raise ValidationError({"description": "Користувач не знайдений"})

            if not check_password(password, user.password):
                raise ValidationError({"description": "Неправильний пароль"})

            refresh = RefreshToken.for_user(user)
            accsess = str(refresh.access_token)

            return Response(
                {
                    "description": "Користувач увійшов в систему",
                    "access_token": accsess,
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                {"description": f"Помилка при вході в систему {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Reset password",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "New password"},
                    "confirmPassword": {
                        "type": "string",
                        "description": "Confirm new password",
                    },
                },
                "required": ["password", "confirmPassword"],
            }
        },
        tags=["Authentication"],
        responses={
            200: OpenApiResponse(
                description="Password reset successful",
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Скидання пароля Успішні",
                        }
                    },
                },
            ),
            400: {"description": "Неприпустимий токен"},
            400: {"description": "Невірний запит error"},
            500: {"description": "Помилка сервера"},
        },
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path="reset-password/<str:uidb64>/<str:token>",
    )
    def reset_password(self, request, uidb64, token):
        try:
            new_password_data = json.loads(request.body)
            password = new_password_data["password"]
            confirmPassword = new_password_data["confirmPassword"]
            self.password_validation(password=password, confirmPassword=confirmPassword)
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response(
                    {"description": "Скидання пароля Успішні"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"description": "Неприпустимий токен"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return Response(
                {"description": f"Невірний запит {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Forgot password",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "User email for password reset request",
                    }
                },
                "required": ["email"],
            }
        },
        tags=["Authentication"],
        responses={
            200: OpenApiResponse(
                description="Password reset email sent successfully",
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Електронна пошта була успішно надіслана",
                        }
                    },
                },
            ),
            400: OpenApiResponse(
                description="Invalid request",
                response={
                    "type": "object",
                    "properties": {
                        "descriptiondescription": {
                            "type": "string",
                            "example": "Електронна пошта не існує",
                        }
                    },
                },
            ),
            500: {"description": "Помилка сервера"},
        },
    )
    @action(detail=False, methods=["POST"], url_path="forgot-password")
    def forgot_password(self, request):
        data = json.loads(request.body)
        email = data["email"]
        self.email_validation(email=email)
        try:
            domain = os.environ.get("DOMAIN")
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            password_reset_link = f"{domain}/reset-password/{uid}/{token}"
            send_mail(
                "Скинути пароль",
                f"Клацніть, щоб посилання на скидання пароля : {password_reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({"description": "Електронна пошта була успішно надіслана"})
        except User.DoesNotExist:
            return Response(
                {"description": "Електронна пошта не існує"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Authentication"],
    )
    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=["GET"],
        url_path="is_auth",
    )
    def is_Auth(self, request):
        """
        Check if the user is authenticated.

        This method is used to determine if the user making the request is authenticated or not. It returns a response indicating whether the user is authenticated or not.

        Parameters:
        - request: The HTTP request object.

        Returns:
        - Response: A JSON response containing the authentication status of the user. The response has a single key-value pair, where the key is 'is_authenticated' and the value is a boolean indicating whether the user is authenticated or not.

        Example:
            HTTP GET /is_auth

            Response:
            {
                "is_authenticated": true
            }
        """
        return Response({"is_authenticated": request.user.is_authenticated})


class AdminService(mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    A viewset for admin operations on UserMini instances.

    This viewset provides administrators with the capabilities to list all UserMini instances
    and update specific user details. Access is restricted to authenticated users with admin privileges.

    Attributes:
        permission_classes (list): A list of permissions checks the viewset uses to grant or deny access.
        queryset (QuerySet): The queryset that should be used for listing users, typically all instances of UserMini.
        serializer_class (Serializer): The serializer class used for serializing and deserializing input and output data.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = UserMini.objects.all()
    serializer_class = UserMiniSerializer

    @extend_schema(
        summary="List all UserMini instances",
        description="Retrieves a list of all UserMini instances from the database. This endpoint is accessible only to users with admin privileges.",
        responses={200: UserMiniSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """
        Lists all UserMini instances.

        Provides a list of all UserMini instances available in the database, serialized using the UserMiniSerializer.
        Accessible only by users with admin privileges.

        Parameters:
            request (Request): The incoming HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The list of UserMini instances serialized data with HTTP status code 200 (OK).
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Update a UserMini instance",
        description="Allows administrators to update details of a specific UserMini instance identified by its primary key. The request must contain the data to be updated, validated against the UserToApprove serializer.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "is_approved": {
                        "type": "boolean",
                    },
                },
            }
        },
        responses={
            200: UserMiniSerializer,
            404: {"description": "Користувач не знайдений"},
            500: {"description": "Помилка сервера"},
        },
        methods=["PUT"],
    )
    def update(self, request, pk):
        """
        Updates a specific UserMini instance.

        Allows administrators to update details of a specific UserMini instance identified by its primary key (pk).
        The updated information must be provided in the request data, and is validated against the UserToApprove serializer.

        Parameters:
            request (Request): The incoming HTTP request containing the data to update.
            pk (int): The primary key of the UserMini instance to update.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The updated UserMini instance serialized data with HTTP status code 200 (OK) if successful.
                      An appropriate error message and HTTP status code otherwise, depending on the type of error encountered.

        Raises:
            ValidationError: If the provided data does not pass validation checks.
            UserMini.DoesNotExist: If no UserMini instance is found with the provided pk.
            Exception: For any other unexpected errors during the update process.
        """
        try:
            instance = UserMini.objects.get(pk=pk)
            serializer = UserToApprove(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserMini.DoesNotExist:
            return Response(
                {"description": "Користувач не знайдений"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
