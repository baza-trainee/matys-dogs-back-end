from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from backblaze.b2_utils import initialize_b2api
from backblaze.models import FileModel
from backblaze.b2_utils import converterToWebP
import os


# Create your views here.


@csrf_exempt
@api_view(['POST'])
def upload_image(request, *args, **kwargs):
    file_obj = request.FILES['image']
    if 'image' not in request.FILES:
        return Response({'message': 'image not found'}, status=status.HTTP_400_BAD_REQUEST)

    if not file_obj:
        return Response({'message': 'no image found'}, status=status.HTTP_400_BAD_REQUEST)

    valid_extensions = ('.jpg', '.png', '.jpeg', '.ios')
    if not file_obj.name.endswith(valid_extensions):
        return Response({'message': 'incorrect file format'}, status=status.HTTP_400_BAD_REQUEST)

    if file_obj.size > 2097152:  # 2MB
        return Response({'message': 'image size should not exceed 2MB'}, status=status.HTTP_400_BAD_REQUEST)

    webp_image_name, bucket_name = converterToWebP(file_obj)

    image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
    file_model = FileModel(name=webp_image_name,
                           url=image_url, category='image')
    file_model.save()

    return Response({'message': 'image uploaded successfully',
                     'image_url': image_url
                     }, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
def upload_document(request, *args, **kwargs):
    b2_api = initialize_b2api()
    file_obj = request.FILES['document']
    if 'document' not in request.FILES:
        return Response({'message': 'document not found'}, status=status.HTTP_400_BAD_REQUEST)
    if not file_obj:
        return Response({'message': 'no document found'}, status=status.HTTP_400_BAD_REQUEST)

    valid_extensions = ('.pdf', '.docx', '.doc', '.txt')
    if not file_obj.name.endswith(valid_extensions):
        return Response({'message': 'incorrect file format'}, status=status.HTTP_400_BAD_REQUEST)

    if file_obj.size > 2097152:  # 2MB
        return Response({'message': 'document size should not exceed 2MB'}, status=status.HTTP_400_BAD_REQUEST)

    bucket_name = os.getenv('BUCKET_NAME_DOC')
    bucket = b2_api.get_bucket_by_name(bucket_name=bucket_name)
    bucket.upload_bytes(file_obj.read(), file_name=file_obj.name)
    document_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{file_obj.name}'
    file_model = FileModel(
        name=file_obj.name, url=document_url, category='document')
    file_model.save()
    return Response({'message': 'document uploaded successfully', 'document_url': document_url}, status=status.HTTP_201_CREATED)
