import unittest

from django.test import TestCase
from django.urls import reverse
import json
from . import views


class ViewsTestCase(TestCase):


    def test_register_view(self):
        # test with valid data
        data = {
            'email': 'test@example.com',
            'password': 'Password123@'
        }
        response = self.client.post(reverse('register'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # test with invalid data
        data = {
            'email': 'test!@example.com',
            'password': 'password'
        }
        response = self.client.post(reverse('register'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_view(self):
        # test with valid data
        data = {
            'email': 'test@example.com',
            'password': 'Password123@'
        }
        response = self.client.post(reverse('login'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # test with invalid data
        data = {
            'email': 'tes!t@example.com',
            'password': 'password'
        }
        response = self.client.post(reverse('login'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
