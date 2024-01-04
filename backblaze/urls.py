from django.urls import path
from backblaze.views import upload_image, upload_document, delete_file
urlpatterns = [
    path('images', upload_image, name='upload_image'),
    path('documents', upload_document, name='upload_document'),
    path(':id', delete_file, name='delete_file')
]
