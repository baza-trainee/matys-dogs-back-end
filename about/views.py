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
from drf_spectacular.utils import extend_schema
import json
# get about data


class AboutList(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            about_data = AboutModel.objects.all()
            serializer = AboutSerializer(about_data, many=True)
            return Response({'about_data': serializer.data}, status=status.HTTP_200_OK)
        except AboutModel.DoesNotExist:
            return Response({'message': 'About data not found'})


# About Images
class AboutImages(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="List all images in AboutModel",
        responses={200: ImagesSerializer(many=True), 404: 'Images not found'}
    )
    def list(self, request):
        try:
            images = AboutModel.objects.all()
            serialized_images = ImagesSerializer(images, many=True)
            return Response(serialized_images.data)
        except AboutModel.DoesNotExist:
            return Response({'message': 'Images not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Create a new image entry in AboutModel",
        responses={201: FileSerializer, 404: 'Файл не знайдено'}
    )
    def create(self, request):
        try:
            # get data from request
            images = request.FILES.getlist('images')
            # add images to about
            about = AboutModel.objects.get(id=2)
            # convert images to webp
            for image in images:
                webp_image_name, webp_image_id, bucket_name, _ = converter_to_webP(
                    image)
                image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'

                try:
                    file_model, created = FileModel.objects.get_or_create(id=webp_image_id,
                                                                          defaults={
                                                                              'name': webp_image_name,
                                                                              'url': image_url,
                                                                              'category': 'image'}
                                                                          )
                    about.images.add(file_model)
                except FileModel.DoesNotExist:
                    return Response({'message': 'Файл не знайдено'}, status=status.HTTP_404_NOT_FOUND)
            # serialize about
            serializer = FileSerializer(file_model)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except AboutModel.DoesNotExist:
            return Response({'message': 'AboutModel entry not found'}, status=status.HTTP_404_NOT_FOUND)
        except FileModel.DoesNotExist:
            return Response({'message': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Delete an image from AboutModel",
        responses={200: 'Зображення видалено', 404: 'Файл не знайдено'}
    )
    def destroy(self, request, pk):
        try:
            about = AboutModel.objects.get(id=2)
            file = FileModel.objects.get(id=pk)
            # check if file and about exist
            if not file or not about:
                return Response({'message': 'Файл не знайдено'}, status=status.HTTP_404_NOT_FOUND)

            file.delete()
            about.images.remove(pk)
            return Response({'message': 'Image deleted'}, status=status.HTTP_200_OK)
        except FileModel.DoesNotExist:
            return Response({'message': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        except AboutModel.DoesNotExist:
            return Response({'message': 'AboutModel entry not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Employment data
class AboutEmployment(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = AboutModel.objects.all()
    serializer_class = EmploymentSerializer

    @extend_schema(
        description="Get employment data from AboutModel",
        request=EmploymentSerializer,
        responses={
            200: EmploymentSerializer,
            500: {'description': 'Internal Server Error'}
        }
    )
    def get(self, request):
        try:
            about = AboutModel.objects.all()
            serializer = EmploymentSerializer(about, many=True)
            return Response({'employment-data': serializer.data})
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Update employment data
    @extend_schema(
        description="Update employment data in AboutModel",
        request=EmploymentSerializer,
        responses={
            200: EmploymentSerializer,
            404: {'description': 'About data not found'},
            500: {'description': 'Internal Server Error'}
        }
    )
    def update(self, request):
        data = json.loads(request.body)
        try:
            about = AboutModel.objects.get(id=2)

            about.quantity_of_animals = data.get(
                'quantity_of_animals', about.quantity_of_animals)
            about.quantity_of_employees = data.get(
                'quantity_of_employees', about.quantity_of_employees)
            about.quantity_of_succeeds_adoptions = data.get(
                'quantity_of_succeeds_adoptions', about.quantity_of_succeeds_adoptions)

            about.save()
            serializer = EmploymentSerializer(about)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AboutModel.DoesNotExist:
            return Response({'message': 'About data not found'})
        except Exception as e:
            return Response({'message': f'Помилка {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
