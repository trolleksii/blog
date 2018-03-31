from time import sleep

from django.test import TestCase, RequestFactory
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

    def test_all_correct(self):
        token = self.user.token
        request = RequestFactory().get('/')
        request.META['HTTP_AUTHORIZATION'] = '{} {}'.format(JWTAuthentication.keyword, token)
        auth_user, auth_token = JWTAuthentication().authenticate(request)
        # should be same user
        self.assertEqual(auth_user, self.user)
        # but different token
        self.assertNotEqual(auth_token, token)

    def test_deleted_user(self):
        token = self.user.token
        self.user.delete()
        request = HttpRequest()
        request.META['HTTP_AUTHORIZATION'] = '{} {}'.format(JWTAuthentication.keyword, token)
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)

    def test_inactive_user(self):
        token = self.user.token
        self.user.is_active = False
        self.user.save()
        request = HttpRequest()
        request.META['HTTP_AUTHORIZATION'] = '{} {}'.format(JWTAuthentication.keyword, token)
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)

    def test_no_auth_header(self):
        request = HttpRequest()
        result = JWTAuthentication().authenticate(request)
        self.assertIsNone(result)

    def test_header_without_token(self):
        token = self.user.token
        self.user.delete()
        request = HttpRequest()
        request.META['HTTP_AUTHORIZATION'] = JWTAuthentication.keyword
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)

    def test_token_with_spaces(self):
        token = self.user.token
        request = HttpRequest()
        request.META['HTTP_AUTHORIZATION'] = '{} {} {}'.format(
            JWTAuthentication.keyword,
            token[:5],
            token[:6]
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
        request = HttpRequest()
        request.META['HTTP_AUTHORIZATION'] = '{} {}'.format(JWTAuthentication.keyword, token)
        sleep(1)
        with self.assertRaises(exceptions.AuthenticationFailed):
            user, token = JWTAuthentication().authenticate(request)
