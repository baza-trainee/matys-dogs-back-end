from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from backblaze.views import upload_image, upload_document

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()

    def test_upload_image(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post('/upload/images', {'image': image})
        self.assertEqual(response.status_code, 201)

    def test_upload_document(self):
        document = SimpleUploadedFile("test_document.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post('/upload/documents', {'document': document})
        self.assertEqual(response.status_code, 201)
