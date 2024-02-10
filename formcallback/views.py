from rest_framework import mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.models import IsApprovedUser
from rest_framework.response import Response
from .serializer import UserCallBack, Notice, NoticeUpdateSerializer
from .models import CallbackForm
from rest_framework.viewsets import GenericViewSet
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
# Create your views here.


class CallBackPost(mixins.CreateModelMixin, GenericViewSet):
    """
    A viewset for creating callback posts from users. This viewset allows any user to submit
    callback requests with their name, phone number, optional comment, and the ID of the dog
    they are interested in.
    """
    permission_classes = [AllowAny]
    queryset = CallbackForm.objects.all()
    serializer_class = UserCallBack

    @extend_schema(
        summary="Update notification",
        description='Update notification status',
        request={
            'multipart/form-data': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                        },
                        'phone_number': {
                            'type': 'string',
                        },
                        'comment': {
                            'type': 'string',
                        },
                        'dog_id': {
                            'type': 'integer',
                        }
                    },
                'required': ['name', 'phone_number', 'dog_id'],
            }
        },
        responses={200: Notice, 400: 'Bad request',
                   500: 'Internal server error'}
    )
    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new callback request. Validates the request data and saves
        the new callback form if valid. Returns the created callback form data on success.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class NotificationAdmin(mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    A viewset for admin users to list and update notifications. Access is restricted to authenticated
    and approved users only. Supports listing all notifications and updating the status of individual notifications.
    """
    permission_classes = [IsAuthenticated, IsApprovedUser]
    queryset = CallbackForm.objects.all()
    serializer_class = Notice

    @extend_schema(
        summary='Get notification list',
        description='Get notification list',
        responses={200: Notice}
    )
    def list(self, request, *args, **kwargs):
        """
        Lists all notifications. This method is accessible only by authenticated and approved users.
        Returns a list of all callback form submissions.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Update notification",
        description='Update notification status',
        request={
            'multipart/form-data': {
                    'type': 'object',
                    'properties': {
                        'status': {
                            'type': 'boolean',
                        },
                        'processing': {
                            'type': 'boolean',
                        },
                        'is_read': {
                            'type': 'boolean',
                        }
                    }
            }
        },
        responses={200: Notice, 400: 'Bad request',
                   500: 'Internal server error'}
    )
    def update(self, request, pk, *args, **kwargs):
        """
        Updates the status of a notification identified by its primary key. Validates the request data
        and applies the updates if valid. Returns the updated notification data on success.
        """
        try:
            instance = CallbackForm.objects.get(pk=pk)
            serializer = NoticeUpdateSerializer(
                instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError:
            return Response({'message': 'Поганий запит - недійсні дані'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
