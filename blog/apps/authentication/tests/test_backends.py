from django.test import TestCase, RequestFactory

from apps.authentication.models import User
from apps.authentication.backends import JWTAuthentication


class AuthBackendTests(TestCase):

    def test_correct_use_auth(self):
        user = User.objects.create(
            username='User1',
            password='qwerty123'
        )
        token = user.token
        request = RequestFactory().get('/')
        request.META['HTTP_AUTHORIZATION'] = '{} {}'.format(JWTAuthentication.keyword, token)
        auth_user, auth_token = JWTAuthentication().authenticate(request)
        # should be same user
        self.assertEqual(auth_user, user)
        # but different token
        self.assertNotEqual(auth_token, token)
