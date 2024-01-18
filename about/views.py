from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from about.models import AboutModel
from backblaze.utils.b2_utils import converter_to_webP
from about.serializer import AboutSerializer
from rest_framework import status
from backblaze.models import FileModel

# get about data


@api_view(['GET'])
@csrf_exempt
def about(request):
    try:
        about_data = AboutModel.objects.all()
        serializer = AboutSerializer(about_data, many=True)
        return Response({'about_data': serializer.data}, status=status.HTTP_200_OK)
    except AboutModel.DoesNotExist:
        return Response({'message': 'About data not found'}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['GET', 'POST', 'PUT', 'DELETE'])
# @permission_classes([IsAuthenticated])
class About(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request):
        # get data from request
        data = request.data
        images = request.FILES.getlist('images')
        # create about
        about = AboutModel.objects.create(quantity_of_animals=data['quantity_of_animals'],
                                          quantity_of_employees=data['quantity_of_employees'],
                                          quantity_of_succeeds_adoptions=data['quantity_of_succeeds_adoptions'])
        # add images to about
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
        serializer = AboutSerializer(about)
        return Response({'about_data': serializer.data}, status=status.HTTP_201_CREATED
                        )

    def put(self, request, pk):
        pass

    def delete(self, request, pk):
        pass
