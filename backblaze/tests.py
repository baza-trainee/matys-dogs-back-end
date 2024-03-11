from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from .models import FileModel
from django.contrib.auth.models import User


class FileManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.get(email='jabsoluty@gmail.com', passowrd='')
        self.client.force_authenticate(user=self.user)

    def test_upload_image_success(self):
        # Assuming you have a way to simulate a valid image file
        url = reverse('upload_image')  # Replace with your actual URL name
        data = {'image': 'your_simulated_image_file'}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Additional tests for image validation failure, webp conversion failure

    def test_upload_document_success(self):
        # Assuming you have a way to simulate a valid document file
        url = reverse('upload_document')  # Replace with your actual URL name
        data = {'document': 'your_simulated_document_file'}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Additional tests for document validation failure, upload process failure

    def test_delete_file_success(self):
        # Create a test file in the database
        test_file = FileModel.objects.create(...)
        # Replace with your actual URL name
        url = reverse('delete_file', args=[test_file.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Additional tests for handling non-existent files, deletion process failure
