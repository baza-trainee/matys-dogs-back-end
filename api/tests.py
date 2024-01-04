from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import json


class UserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='admin', email='adminuser@example.com', password='User!234')

    def test_register(self):
        response = self.client.post('/register', json.dumps({
            'email': 'adminuser@example.com',
            'password': 'User!234',
            'confirmPassword': 'User!234'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['email'], 'adminuser@example.com')

    def test_login(self):
        response = self.client.post('/login', json.dumps({
            'email': 'adminuser@example.com',
            'password': 'User!234'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('accsess', response.json())
