import jwt

from time import sleep
from django.test import TestCase
from django.core.exceptions import ValidationError

from blog.settings import SECRET_KEY

from apps.authentication.models import User


class AuthModelTests(TestCase):

    def test_add_user_with_all_fields(self):
        user = User(
            username='TestUser',
            email='testuser@somemail.com',
            password='qwerty123'
        )
        user.full_clean()
        user.save()

    def test_str_method(self):
        user = User.objects.create_user(
            username='kenny',
            password='qwerty123'
        )
        self.assertEqual(str(user), user.username)

    def test_add_user_wrong_email(self):
        with self.assertRaises(Exception):
            user = User(
                username='TestUser',
                email='testuser_at_somemail.com',
                password='qwerty123'
            )
            user.full_clean()

    def test_cant_create_duplicate(self):
        User.objects.create(
            username='TestUser',
            password='qwerty123'
        )
        with self.assertRaises(ValidationError):
            user = User(
                username='TestUser',
                password='qwerty123'
            )
            user.full_clean()

    def test_jwt_is_generated(self):
        user = User.objects.create(
            username='TestUser',
            password='qwerty123'
        )
        self.assertIsNotNone(user.token)

    def test_jwt_decodes(self):
        user = User.objects.create(
            username='TestUser',
            password='qwerty123'
        )
        expected_pk = user.pk
        data = jwt.decode(user.token, SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(data['id'], expected_pk)

    def test_expired_token(self):
        user = User(
            username='TestUser',
            password='qwerty123',
            token_valid_for=0
        )
        user.full_clean()
        user.save()
        token = user.token
        sleep(1)
        with self.assertRaises(jwt.exceptions.ExpiredSignatureError):
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
