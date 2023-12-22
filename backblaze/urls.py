from . import views
from django.urls import path, include
from backblaze.views import upload_image
urlpatterns = [
    path('test', views.test, name='test'),
    path('images', upload_image, name='images')
]
