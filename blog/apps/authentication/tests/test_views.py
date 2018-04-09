import json

from django.shortcuts import reverse
from django.test import TestCase

from apps.authentication.models import User


class RegistrationViewTests(TestCase):

    def test_correct_data(self):
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

    def test_duplicate_user(self):
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
        errors = response2.data.get('errors', None)
        error = errors.get('username', None)
        self.assertIsNotNone(error)

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
        errors = response.data.get('errors', None)
        self.assertIsNotNone(errors)
        email_error = errors.get('email', None)
        self.assertIsNotNone(email_error)
        password_error = errors.get('password', None)
        self.assertIsNotNone(password_error)


class LoginViewTests(TestCase):

    fixtures = ['authentication.json']

    def test_user_login(self):
        data = json.dumps(
            {
                "user": {
                    "username": "kenny",
                    "password": "qwerty123",
                }
            }
        )
        response = self.client.post(
            reverse('authentication:login_view'),
            data=data,
            content_type='application/json'
        )
        user = response.data.get('user', None)
        self.assertIsNotNone(user)

    def test_wrong_password(self):
        data = json.dumps(
            {
                "user": {
                    "username": "kenny",
                    "password": "qwerty1234",
                }
            }
        )
        response = self.client.post(
            reverse('authentication:login_view'),
            data=data,
            content_type='application/json'
        )
        user = response.data.get('user', None)
        self.assertIsNone(user)


class UserViewTests(TestCase):

    fixtures = ['authentication.json']

    def test_get_user_info(self):
        user = User.objects.first()
        token = user.token
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + token
        }
        response = self.client.get(
            reverse('authentication:retrieve_view'), **headers)
        user_data = response.data.get('user', None)
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['username'], user.username)
        self.assertEqual(user_data['about'], user.profile.about)
        self.assertEqual(user_data['pic'], user.profile.pic)

    def test_get_user_info_wrong_token(self):
        headers = {
            'HTTP_AUTHORIZATION': 'Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NCwiZXhwIjoxNTIyNTY5MDQ2Ljg2NjYxfQ.EdbIIn7Xnz7c5YL-Eo-5VdcORnmhK3JQSUMZL6Sjn5W'
        }
        response = self.client.get(
            reverse('authentication:retrieve_view'), **headers)
        user_data = response.data.get('user', None)
        self.assertIsNone(user_data)
        errors = response.data.get('errors', None)
        self.assertIsNotNone(errors)

    def test_update_user_info(self):
        new_email = 'kenneth@gmail.com'
        new_about = 'Every decent mock person requires decent name.'
        token = User.objects.first().token
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + token,
        }
        data = json.dumps({
            'user': {
                'email': new_email,
                'about': new_about
            }
        })
        response = self.client.put(
            reverse('authentication:retrieve_view'),
            data=data,
            content_type='application/json',
            **headers
        )
        user_data = response.data.get('user', None)
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['email'], new_email)
        self.assertEqual(user_data['about'], new_about)
        user = User.objects.first()
        self.assertEqual(user.email, new_email)
        self.assertEqual(user.profile.about, new_about)
