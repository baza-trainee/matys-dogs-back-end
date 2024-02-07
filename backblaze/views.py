from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from backblaze.models import FileModel
from backblaze.utils.b2_utils import converter_to_webP, delete_file_from_backblaze
from backblaze.utils.validation import image_validation
from rest_framework.validators import ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from api.models import IsApprovedUser
from about.models import AboutModel as About
from backblaze.serializer import FileSerializer
# Create your views here.


class UploadImage(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated, IsApprovedUser]

    serializer_class = FileSerializer

    def get_queryset(self):
        about_instanse = About.objects.first()
        if about_instanse:
            return about_instanse.images.all()
        else:
            return FileModel.objects.none()

    # get images

    def list(self, request):
        queryset = self.get_queryset()
        serializer = FileSerializer(queryset, many=True)
        return Response(serializer.data)

    # upload image
    def create(self, request):
        uploaded_files = request.FILES.getlist('image')
        response_data = []

        for file_obj in uploaded_files:
            try:

                # Convert image to webp
                webp_image_name, webp_image_id, image_url = converter_to_webP(
                    file_obj)

                # Save image to database
                file_model = FileModel(id=webp_image_id, name=webp_image_name,
                                       url=image_url, category='image')
                file_model.save()

                response_data.append({
                    'message': 'Зображення успішно завантажено',
                    'image_url': image_url,
                    'image_id': webp_image_id,
                    'image_name': webp_image_name,
                })

            except ValidationError as e:
                response_data.append({'error': str(e)})

        return Response(response_data, status=status.HTTP_200_OK if response_data else status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, file_id):
        try:
            # Get file from database
            file_model = FileModel.objects.get(id=file_id)
            if not file_model:
                delete_file_from_backblaze(file_id)
                return Response({'message': 'Файл успішно видалено'}, status=status.HTTP_200_OK)

            # Delete file from Backblaze
            delted_file = delete_file_from_backblaze(file_id)
            if not delted_file:
                file_model.delete()
                return Response({'message': 'Файл успішно видалено'}, status=status.HTTP_200_OK)

            # Delete file from database
            if delted_file:
                file_model.delete()
                return Response({'message': 'Файл успішно видалено', 'file_name': delted_file.file_name, 'file_id': delted_file.file_id}, status=status.HTTP_200_OK)
        except FileModel.DoesNotExist:
            return Response({'error': 'Файл не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Неочікувана помилка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
