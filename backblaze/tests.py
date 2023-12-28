from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from backblaze.models import FileModel
from backblaze.views import upload_image, upload_document
import os
test_image_path = os.getenv('TEST_IMAGE_PATH')
test_document_path = os.getenv('TEST_DOCUMENT_PATH')


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_upload_image(self):
        with open(test_image_path, 'rb') as image:
            response = self.client.post('/upload/images', {'image': image})
            self.assertEqual(response.status_code, 201)
            self.assertIn('image uploaded successfully',
                          response.content.decode())

    def test_upload_document(self):
        with open(test_document_path, 'rb') as document:
            response = self.client.post(
                '/upload/documents', {'document': document})
            self.assertEqual(response.status_code, 201)
            self.assertIn('document uploaded successfully',
                          response.content.decode())

    def test_upload_image_no_image(self):
        response = self.client.post('/upload/images')
        self.assertEqual(response.status_code, 400)
        self.assertIn('image not found', response.content.decode())

    def test_upload_document_no_document(self):
        response = self.client.post('/upload/documents')
        self.assertEqual(response.status_code, 400)
        self.assertIn('document not found', response.content.decode())

    def test_upload_image_incorrect_format(self):
        image = SimpleUploadedFile('wrong_format.txt', b'file_content')
        response = self.client.post('/upload/images', {'image': image})
        self.assertEqual(response.status_code, 400)
        self.assertIn('incorrect file format', response.content.decode())

    def test_upload_document_incorrect_format(self):
        document = SimpleUploadedFile('wrong_format.jpg', b'file_content')
        response = self.client.post(
            '/upload/documents', {'document': document})
        self.assertEqual(response.status_code, 400)
        self.assertIn('incorrect file format', response.content.decode())

    def test_upload_image_exceed_size(self):
        image = SimpleUploadedFile('large_image.jpg', b'file_content'*4000000)
        response = self.client.post('/upload/images', {'image': image})
        self.assertEqual(response.status_code, 400)
        self.assertIn('image size should not exceed 2MB',
                      response.content.decode())

    def test_upload_document_exceed_size(self):
        document = SimpleUploadedFile(
            'large_document.pdf', b'file_content'*4000000)
        response = self.client.post(
            '/upload/documents', {'document': document})
        self.assertEqual(response.status_code, 400)
        self.assertIn('document size should not exceed 2MB',
                      response.content.decode())
