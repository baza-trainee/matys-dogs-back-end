from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from about.models import AboutModel
from rest_framework.permissions import AllowAny
from backblaze.utils.b2_utils import converter_to_webP
from about.serializer import AboutSerializer, ImagesSerializer, EmploymentSerializer
from rest_framework import status
from backblaze.models import FileModel
from backblaze.serializer import FileSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.validators import ValidationError
from api.models import IsApprovedUser
import json

# get about data


class AboutList(mixins.ListModelMixin, GenericViewSet):
    """
    A viewset for listing the about data from the AboutModel. This class provides an endpoint
    for retrieving general information about the organization or entity.
    """
    permission_classes = [AllowAny]
    queryset = AboutModel.objects.all()
    serializer_class = AboutSerializer

    @extend_schema(
        summary='Retrieve about data',
        description="Retrieve about data",
        responses={
            200: AboutSerializer(many=True),
        }
    )
    def list(self, request):
        """
        Retrieves about data from the AboutModel. This method provides a way to fetch and serialize
        about data, making it available through a GET request.

        Args:
            request: HttpRequest object.

        Returns:
            Response: Serialized about data encapsulated within a Response object, including HTTP status.
        """
        about_data = self.get_queryset()
        serializer = self.get_serializer(about_data, many=True)
        return Response({'about_data': serializer.data}, status=status.HTTP_200_OK)


# About Images
class AboutImages(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    """
    A viewset for managing image data related to the AboutModel. It supports listing all images,
    creating new image entries by uploading and converting images to webP format, and deleting existing images.
    """
    permission_classes = [IsAuthenticated, IsApprovedUser]
    queryset = AboutModel.objects.all()
    serializer_class = ImagesSerializer

    @extend_schema(
        summary='List all images in AboutModel',
        description="List all images in AboutModel",
        responses={200: ImagesSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """
        Lists all images associated with the AboutModel. Utilizes the configured serializer to return
        a serialized list of images.

        Args:
            request: HttpRequest object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HttpResponse with the serialized list of images.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Create a new image entry in AboutModel',
        description="Adds new image entries to the AboutModel instance, converting them to webP format.",
        responses={
            201: FileSerializer(many=True),
            400: {'description': 'Bad request'},
        }
    )
    def create(self, request):
        """
        Creates a new image entry or entries in the AboutModel by uploading images. Uploaded images are
        automatically converted to webP format. Supports bulk upload.

        Args:
            request: HttpRequest object containing the images to upload in the FILES attribute.

        Returns:
            Response: An HttpResponse indicating the outcome of the create operation, including the data
            of the created image entries on success or an error message on failure.
        """
        try:
            images = request.FILES.getlist('images')
            created_files = []
            if not images:
                return Response({'message': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)

            about = AboutModel.objects.filter(id=2).first()

            for image in images:
                webp_image_name, webp_image_id, image_url = converter_to_webP(
                    image)
                file_model, created = FileModel.objects.get_or_create(
                    id=webp_image_id,
                    defaults={
                        'name': webp_image_name,
                        'url': image_url,
                        'category': 'image'
                    }
                )
                about.images.add(file_model)
                created_files.append(file_model)

            serializer = FileSerializer(created_files, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary='Delete an image from AboutModel',
        description="Delete an image from AboutModel",
        responses={200: 'Зображення видалено', 404: 'Файл не знайдено'}
    )
    def destroy(self, request, pk):
        """
        Deletes an image entry from the AboutModel by its primary key (pk). This also involves removing
        the image from the associated AboutModel instance and deleting the image file.

        Args:
            request: HttpRequest object.
            pk: Primary key of the image to delete.

        Returns:
            Response: An HttpResponse indicating success or failure of the delete operation.
        """
        try:
            about = AboutModel.objects.filter(id=2).first()
            file = FileModel.objects.get(pk=pk)
            file.delete()
            about.images.remove(pk)
            return Response({'message': 'Image deleted'}, status=status.HTTP_200_OK)
        except FileModel.DoesNotExist:
            return Response({'message': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Employment data
class AboutEmployment(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    """
    A viewset for managing employment data related to the AboutModel. It provides endpoints for
    retrieving and updating employment-related information.
    """
    permission_classes = [IsAuthenticated, IsApprovedUser]
    queryset = AboutModel.objects.all()
    serializer_class = EmploymentSerializer

    @extend_schema(
        summary='Get employment data from AboutModel',
        description="Get employment data from AboutModel",
        request=EmploymentSerializer,
        responses={
            200: EmploymentSerializer,
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieves employment data from the AboutModel. This method allows for fetching and serializing
        employment-related information, accessible via a GET request.

        Args:
            request: HttpRequest object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: Serialized employment data encapsulated within a Response object.
        """
        return super().list(request, *args, **kwargs)

    # Update employment data

    @extend_schema(
        summary='Update employment data in AboutModel',
        description="Update employment data in AboutModel",
        request=EmploymentSerializer,
        responses={
            200: EmploymentSerializer,
            400: {'description': 'Поганий запит - недійсні дані'},
            500: {'description': 'Внутрішня помилка сервера'}
        }
    )
    def update(self, request):
        """
        Updates employment data in the AboutModel. This method allows for modifying details like
        the quantity of employees, animals, and successful adoptions.

        Args:
            request: HttpRequest object containing the updated employment data in its body.

        Returns:
            Response: An HttpResponse indicating the outcome of the update operation, including the updated
            data on success or an error message on failure.
        """
        data = json.loads(request.body)
        try:
            about = AboutModel.objects.filter(id=2).first()

            about.quantity_of_animals = data.get(
                'quantity_of_animals', about.quantity_of_animals)
            about.quantity_of_employees = data.get(
                'quantity_of_employees', about.quantity_of_employees)
            about.quantity_of_succeeds_adoptions = data.get(
                'quantity_of_succeeds_adoptions', about.quantity_of_succeeds_adoptions)

            about.save()
            serializer = EmploymentSerializer(about)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError:
            return Response({'message': 'Поганий запит - недійсні дані'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
