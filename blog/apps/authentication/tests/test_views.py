import json

from django.shortcuts import reverse

from django.test import TestCase


class RegistrationViewTests(TestCase):

    def test_register_user(self):
        data = json.dumps(
            {
                "user": {
                    "username": "kenny",
                    "password": "qwerty123",
                    "email": "kenny@spmail.com"
                }
            }
        )
        response = self.client.post(
            reverse('authentication:register_view'),
            data=data,
            content_type='application/json'
        )
        user = response.data.get('user', None)
        self.assertIsNotNone(user)
        token = user.get('token', '')
        self.assertNotEqual(token, '')

    def test_register_duplicate(self):
        data = json.dumps(
            {
                "user": {
                    "username": "kenny",
                    "password": "qwerty123",
                    "email": "kenny@spmail.com"
                }
            }
        )
        response1 = self.client.post(
            reverse('authentication:register_view'),
            data=data,
            content_type='application/json'
        )
        user = response1.data.get('user', None)
        self.assertIsNotNone(user)

        response2 = self.client.post(
            reverse('authentication:register_view'),
            data=data,
            content_type='application/json'
        )
        error = response2.data.get('username', None)
        self.assertEqual(error, ['A user with that username already exists.'])

    def test_fields_constrains(self):
        data = json.dumps(
            {
                "user": {
                    "username": "kenny",
                    "password": "qwerty",
                    "email": "kennymail"
                }
            }
        )
        response = self.client.post(
            reverse('authentication:register_view'),
            data=data,
            content_type='application/json'
        )
        error = response.data.get('email', None)
        self.assertEqual(error, ['Enter a valid email address.'])
        error = response.data.get('password', None)
        self.assertEqual(error, ['Ensure this field has at least 8 characters.'])


class LoginViewTests(TestCase):

    # fixtures = 'fixtures.json'

    def test_user_login(self):
        pass


class UserViewTests(TestCase):

    # fixtures = 'fixtures.json'

    def test_get_user_info(self):
        pass
