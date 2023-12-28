from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from backblaze.models import FileModel
from backblaze.utils.b2_utils import converterToWebP, documentSimplifyUpd
from backblaze.utils.validation import image_validation, document_validation


# Create your views here.


@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    file_obj = request.FILES['image']
    image_validation(file_obj)

    webp_image_name, bucket_name = converterToWebP(file_obj)

    image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
    file_model = FileModel(name=webp_image_name,
                           url=image_url, category='image')
    file_model.save()

    return Response({'message': 'image uploaded successfully',
                    'image_url': image_url
                     }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def upload_document(request):
    file_obj = request.FILES['document']
    document_validation(file_obj)

    file_name, bucket_name = documentSimplifyUpd(file_obj)

    document_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{file_name}'
    file_model = FileModel(
        name=file_name, url=document_url, category='document')
    file_model.save()
    return Response({'message': 'document uploaded successfully', 'document_url': document_url}, status=status.HTTP_200_OK)
