from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import HttpResponse
from b2sdk.v1 import *
import os
# Create your views here.


@csrf_exempt
@api_view(['POST'])
def upload_image(request, *args, **kwargs):
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    application_key_id = os.getenv('APPLICATION_KEY_ID')
    application_key = os.getenv('APPLICATION_KEY')
    b2_api.authorize_account(
        "production", application_key_id, application_key)
    if 'image' not in request.FILES:
        return Response({'message': 'image not found'}, status=status.HTTP_400_BAD_REQUEST)
    file_obj = request.FILES['image']
    if file_obj.size > 2097152:  # 2MB
        return Response({'message': 'image size should not exceed 5MB'}, status=status.HTTP_400_BAD_REQUEST)

    if not file_obj:
        return Response({'message': 'no image found'}, status=status.HTTP_400_BAD_REQUEST)

    if not file_obj.name.endswith(('.jpg', '.png', '.jpeg', '.ios')):
        return Response({'message': 'incorect file format'}, status=status.HTTP_400_BAD_REQUEST)

    bucket_name = os.getenv('YOUR_BUCKER_NAME')
    bucket = b2_api.get_bucket_by_name(bucket_name=bucket_name)
    bucket.upload_bytes(file_obj.read(), file_name=file_obj.name, )

    return Response({'message': 'image uploaded successfully', 'image_url': f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{file_obj.name}'}, status=status.HTTP_201_CREATED)


# @csrf_exempt
# @api_view(['POST'])
# def upload_image(request):
#     image = request.FILES['image']
#     file_name = image.name
#     bucket = b2_api.get_bucket_by_name(os.getenv('YOUR_BUCKER_NAME'))
#     bucket.upload_local_file(local_file=file_name, file_name=file_name)
#     return Response({'message': 'image uploaded successfully'})


@csrf_exempt
@api_view(['GET'])
def test(request):
    return HttpResponse('this is new image route')
