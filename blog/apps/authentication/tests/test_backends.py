from time import sleep

from django.test import TestCase
from django.http.request import HttpRequest

from rest_framework.authentication import exceptions

from apps.authentication.models import User
from apps.authentication.backends import JWTAuthentication


class AuthBackendTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='User1',
            password='qwerty123'
        )

    def _create_request_with_auth_header(self, token):
        request = HttpRequest()
        request.META['HTTP_AUTHORIZATION'] = '{} {}'.format(JWTAuthentication.keyword, token)
        return request

    def test_all_correct(self):
        token = self.user.token
        request = self._create_request_with_auth_header(token)
        auth_user, auth_token = JWTAuthentication().authenticate(request)
        self.assertEqual(auth_user, self.user)
        self.assertNotEqual(auth_token, token)

    def test_deleted_user(self):
        token = self.user.token
        self.user.delete()
        request = self._create_request_with_auth_header(token)
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)

    def test_inactive_user(self):
        token = self.user.token
        self.user.is_active = False
        self.user.save()
        request = self._create_request_with_auth_header(token)
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)

    def test_no_auth_header(self):
        request = HttpRequest()
        result = JWTAuthentication().authenticate(request)
        self.assertIsNone(result)

    def test_token_of_deleted_user(self):
        token = self.user.token
        self.user.delete()
        request = self._create_request_with_auth_header(token)
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)

    def test_header_without_token(self):
        request = self._create_request_with_auth_header('')
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)

    def test_token_with_spaces(self):
        token = self.user.token
        request = self._create_request_with_auth_header(
            '{} {}'.format(token[:5], token[:6])
        )
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)

    def test_expired_token(self):
        user = User.objects.create_user(
            username='TestUser',
            password='qwerty123',
            token_valid_for=0
        )
        token = user.token
        request = self._create_request_with_auth_header(token)
        sleep(1)
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)
