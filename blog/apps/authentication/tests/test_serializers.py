from django.test import TestCase

from apps.authentication.models import User
from apps.authentication.serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)


class RegisterSerializerTests(TestCase):

    def test_without_email(self):
        data = {
            'username': 'User',
            'password': 'password',
        }
        serializer = RegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        user_exists = User.objects.filter(username='User').exists()
        self.assertTrue(user_exists)

    def test_with_correct_data(self):
        data = {
            'username': 'User',
            'email': 'user@mail.com',
            'password': 'password',
        }
        serializer = RegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        registered_user = serializer.save()
        query_user = User.objects.get(username='User')
        self.assertEqual(registered_user, query_user)

    def test_short_password(self):
        data = {
            'username': 'User',
            'password': 'pass',
        }
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertNotEqual(serializer.errors, {})
        with self.assertRaises(AssertionError):
            serializer.save()

    def test_profile_was_created(self):
        data = {
            'username': 'User',
            'email': 'user@mail.com',
            'password': 'password',
        }
        serializer = RegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertIsNotNone(user.profile)


class LoginSerializerTests(TestCase):

    def setUp(self):
        self.user_credentials = {
            'username': 'kenny',
            'password': 'qwerty123'
        }
        self.user = User.objects.create_user(**self.user_credentials)

    def test_returns_user_data(self):
        serializer = LoginSerializer(data=self.user_credentials)
        self.assertTrue(serializer.is_valid())

    def test_without_username(self):
        self.user_credentials.pop('username')
        serializer = LoginSerializer(data=self.user_credentials)
        self.assertFalse(serializer.is_valid())
        username_error = serializer.errors.get('username', None)
        self.assertIsNotNone(username_error)

    def test_without_password(self):
        self.user_credentials.pop('password')
        serializer = LoginSerializer(data=self.user_credentials)
        self.assertFalse(serializer.is_valid())
        password_error = serializer.errors.get('password', None)
        self.assertIsNotNone(password_error)

    def test_with_wrong_password(self):
        self.user_credentials['password'] = 'wrongpassword'
        serializer = LoginSerializer(data=self.user_credentials)
        self.assertFalse(serializer.is_valid())
        error = serializer.errors
        self.assertNotEqual(error, {})

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        serializer = LoginSerializer(data=self.user_credentials)
        self.assertFalse(serializer.is_valid())
        error = serializer.errors
        self.assertNotEqual(error, [])


class UserSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='SomeUser',
            password='SomePassword'
        )

    def test_partial_update(self):
        serializer = UserSerializer(
            self.user,
            data={'email': 'someuser@mail.com'},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(self.user.email, 'someuser@mail.com')

    def test_full_update_partial_data(self):
        serializer = UserSerializer(
            self.user,
            data={'email': 'someuser@mail.com'}
        )
        self.assertFalse(serializer.is_valid())

    def test_full_update_all_data(self):
        serializer = UserSerializer(
            self.user,
            data={
                'email': 'someuser@mail.com',
                'password': 'NewPassword'
            }
        )
        self.assertTrue(serializer.is_valid())

    def test_update_empty_data(self):
        serializer = UserSerializer(self.user, data={}, partial=True)
        self.assertFalse(serializer.is_valid())

    def test_serializer_updates_profile(self):
        serializer = UserSerializer(
            self.user,
            data={
                'email': 'someuser@mail.com',
                'about': 'my about',
                'pic': 'https://my.pic.com/my.png',
                'password': 'NewPassword'
            }
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(self.user.profile.pic, 'https://my.pic.com/my.png')
        self.assertEqual(self.user.profile.about, 'my about')

    def test_display_user(self):
        serializer = UserSerializer(self.user)
        expected_data = {
            'username': self.user.username,
            'email': '',
            'pic': '',
            'about': ''
        }
        data = serializer.data
        token = data.pop('token', None)
        self.assertNotEqual(token, None)
        self.assertEqual(expected_data, data)
