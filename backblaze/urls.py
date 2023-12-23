from . import views
from django.urls import path, include
from backblaze.views import upload_image, upload_document
urlpatterns = [
    path('images', upload_image, name='upload_image'),
    path('documents', upload_document, name='upload_document')
]
