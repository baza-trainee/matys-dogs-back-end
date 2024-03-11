from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from .models import User
from django.contrib.auth.hashers import make_password


class UserViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')  # Adjust URL name as needed
        self.login_url = reverse('login')  # Adjust URL name as needed
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'confirmPassword': 'password123'
        }
        User.objects.create(email='existing@example.com',
                            password=make_password('password123'))

    def test_register_success(self):
        response = self.client.post(
            self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_existing_user(self):
        existing_user_data = self.user_data.copy()
        existing_user_data['email'] = 'existing@example.com'
        response = self.client.post(
            self.register_url, existing_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_data(self):
        invalid_user_data = self.user_data.copy()
        invalid_user_data['email'] = 'invalid'
        response = self.client.post(
            self.register_url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'email': 'existing@example.com',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_password(self):
        response = self.client.post(self.login_url, {
            'email': 'existing@example.com',
            'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
