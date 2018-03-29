from django.test import TestCase

from apps.authentication.models import User
from apps.authentication.serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)


class RegisterSerializerTests(TestCase):

    def test_user_creation_wo_email(self):
        data = {
            'username': 'User',
            'password': 'password',
        }
        serializer = RegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        serializer.save()
        users = User.objects.filter(username='User')
        self.assertNotEqual(len(users), 0)

    def test_user_creation_with_email(self):
        data = {
            'username': 'User',
            'email': 'user@mail.com',
            'password': 'password',
        }
        serializer = RegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        reg_user = serializer.save()
        query_user = User.objects.get(username='User')
        self.assertEqual(reg_user, query_user)

    def test_user_creation_short_password(self):
        data = {
            'username': 'User',
            'password': 'pass',
        }
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertNotEqual(serializer.errors, {})
        with self.assertRaises(AssertionError):
            serializer.save()

    def test_if_profile_created(self):
        data = {
            'username': 'User',
            'email': 'user@mail.com',
            'password': 'password',
        }
        serializer = RegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        user = serializer.save()
        self.assertIsNotNone(user.profile)


class LoginSerializerTests(TestCase):

    fixtures = ['authentication.json']

    def test_login_returns_user_data(self):
        serializer = LoginSerializer(
            data={'username': 'kenny', 'password': 'qwerty123'})
        self.assertTrue(serializer.is_valid())

    def test_login_without_username(self):
        serializer = LoginSerializer(
            data={'password': 'qwerty123'})
        self.assertFalse(serializer.is_valid())

    def test_login_without_password(self):
        serializer = LoginSerializer(
            data={'username': 'kenny'})
        self.assertFalse(serializer.is_valid())

    def test_login_with_wrong_password(self):
        serializer = LoginSerializer(
            data={'username': 'kenny', 'password': 'qwertyqwe'})
        self.assertFalse(serializer.is_valid())

    def test_login_inactive_user(self):
        serializer = LoginSerializer(
            data={'username': 'inactive_user', 'password': 'qwerty123'})
        self.assertFalse(serializer.is_valid())


class UserSerializerTests(TestCase):

    def setUp(self):
        reg_serializer = RegistrationSerializer(data={
            'username': 'SomeUser',
            'password': 'SomePassword'
        })
        self.assertTrue(reg_serializer.is_valid())
        self.user = reg_serializer.save()

    def test_user_partial_update(self):
        serializer = UserSerializer(
            self.user, data={'email': 'someuser@mail.com'}, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(self.user.email, 'someuser@mail.com')

    def test_update_require_all_data(self):
        serializer = UserSerializer(
            self.user, data={'email': 'someuser@mail.com'})
        self.assertFalse(serializer.is_valid())
        serializer = UserSerializer(self.user, data={
            'email': 'someuser@mail.com',
            'password': 'NewPassword'
        })
        self.assertTrue(serializer.is_valid())

    def test_changes_in_profile(self):
        serializer = UserSerializer(self.user, data={
            'email': 'someuser@mail.com',
            'about': 'my about',
            'pic': 'https://my.pic.com/my.png',
            'password': 'NewPassword'
        })
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(self.user.profile.pic, 'https://my.pic.com/my.png')
        self.assertEqual(self.user.profile.about, 'my about')

    def test_user_display(self):
        serializer = UserSerializer(self.user)
        expected_data = {
            'username': 'SomeUser',
            'email': '',
            'pic': '',
            'about': ''
        }
        data = serializer.data
        token = data.pop('token', None)
        self.assertNotEqual(token, None)
        self.assertEqual(expected_data, data)
