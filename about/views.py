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
from drf_spectacular.utils import extend_schema
from rest_framework.validators import ValidationError
from api.models import IsApprovedUser

# get about data


class AboutList(mixins.ListModelMixin, GenericViewSet):
    """
    A viewset for listing the about data from the AboutModel. This class provides an endpoint
    for retrieving general information about the organization or entity.
    """

    permission_classes = [AllowAny]
    queryset = AboutModel.objects.all().prefetch_related("images")
    serializer_class = AboutSerializer

    @extend_schema(
        summary="Retrieve about data",
        description="Retrieve about data",
        responses={
            200: AboutSerializer(many=True),
        },
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieves about data from the AboutModel. This method provides a way to fetch and serialize
        about data, making it available through a GET request.

        Args:
            request: HttpRequest object.

        Returns:
            Response: Serialized about data encapsulated within a Response object, including HTTP status.
        """
        return super().list(request, *args, **kwargs)


# About Images
class AboutImages(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    """
    A viewset for managing image data related to the AboutModel. It supports listing all images,
    creating new image entries by uploading and converting images to webP format, and deleting existing images.
    """

    permission_classes = [IsAuthenticated, IsApprovedUser]
    queryset = AboutModel.objects.all().prefetch_related("images")
    serializer_class = ImagesSerializer

    @extend_schema(
        summary="List all images in AboutModel",
        description="List all images in AboutModel",
        responses={200: ImagesSerializer(many=True)},
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
        summary="Upload images to AboutModel",
        description="Uploads multiple images to AboutModel, automatically converting them to webP format. Supports bulk upload.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"images": {"type": "string", "format": "binary"}},
            }
        },
        responses={
            201: ImagesSerializer,
            400: {"description": "Зображення не знайдено"},
            400: {"description": "Поганий запит - ValidationError"},
            500: {"description": "Помилка сервера"},
        },
    )
    def create(self, request):
        """
        Creates a new image entry or entries in the AboutModel by uploading images. Uploaded images are
        automatically converted to webP format. Supports bulk upload.

        Args:
            request: HttpRequest object containing the images to upload in the FILES attribute.

        Returns:
            Response: An HttpResponse indicating the outcome of the create operation, including the data
            of the created image entry on success or an error message on failure.
        """
        try:
            images = request.FILES.get("images")
            about = AboutModel.objects.filter(id=2).first()

            if images is None:
                return Response(
                    {"description": "Зображення не знайдено "},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            webp_image_name, webp_image_id, image_url = converter_to_webP(images)
            file_model = FileModel.objects.create(
                id=webp_image_id,
                name=webp_image_name,
                url=image_url,
                category="image",
            )
            about.images.add(file_model)
            serializer = FileSerializer(file_model, many=False)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                {"description": f"Поганий запит - {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Delete an image from AboutModel",
        description="Delete an image from AboutModel",
        responses={
            200: {"description": "Зображення видалено"},
            404: {"description": "Файл не знайдено"},
            500: {"description": "Помилка сервера"},
        },
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
            return Response(
                {"description": "Зображення видалено"}, status=status.HTTP_200_OK
            )
        except FileModel.DoesNotExist:
            return Response(
                {"description": "Файл не знайдено"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
        summary="Get employment data from AboutModel",
        description="Get employment data from AboutModel",
        request=EmploymentSerializer,
        responses={
            200: EmploymentSerializer,
        },
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
        summary="Update employment data in AboutModel",
        description="Update employment data in AboutModel",
        request=EmploymentSerializer,
        responses={
            200: EmploymentSerializer,
            400: {"description": "Поганий запит - ValidationError"},
            500: {"description": "Помилка сервера"},
        },
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
        try:
            instance = AboutModel.objects.filter(id=2).first()
            serializer = EmploymentSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {"description": f"Поганий запит - {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"description": "Помилка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
