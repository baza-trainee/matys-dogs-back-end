from django.urls import path
from backblaze.views import UploadImage

urlpatterns = [
    path('images', UploadImage.as_view(
        {'post': 'create', 'get': 'list'}), name='upload_image'),
    path('<str:file_id>', UploadImage.as_view(
        {'delete': 'destroy'}), name='delete_file'),
]
