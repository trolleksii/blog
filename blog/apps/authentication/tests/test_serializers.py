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
        validity = serializer.is_valid()
        self.assertEqual(validity, True)
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
        validity = serializer.is_valid()
        self.assertEqual(validity, True)
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
        validity = serializer.is_valid()
        self.assertEqual(validity, False)
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
        validity = serializer.is_valid()
        self.assertEqual(validity, True)
        self.assertEqual(serializer.errors, {})
        user = serializer.save()
        self.assertIsNotNone(user.profile)


class LoginSerializerTests(TestCase):

    def setUp(self):
        User.objects.create_user(**{
            'username': 'SomeUser',
            'password': 'SomePassword',
            'email': 'someuser@somedomain.com'
        })
        inactiveuser = User.objects.create_user(**{
            'username': 'InactiveUser',
            'password': 'SomePassword',
            'email': 'someuser@somedomain.com'
        })
        inactiveuser.is_active = False
        inactiveuser.save()

    def test_login_returns_user_data(self):
        serializer = LoginSerializer(
            data={'username': 'SomeUser', 'password': 'SomePassword'})
        result = serializer.is_valid()
        self.assertTrue(result)

    def test_login_without_username(self):
        serializer = LoginSerializer(
            data={'password': 'wrongPassword'})
        result = serializer.is_valid()
        self.assertFalse(result)

    def test_login_without_password(self):
        serializer = LoginSerializer(
            data={'username': 'SomeUser'})
        result = serializer.is_valid()
        self.assertFalse(result)

    def test_login_with_wrong_password(self):
        serializer = LoginSerializer(
            data={'username': 'SomeUser', 'password': 'wrongPassword'})
        result = serializer.is_valid()
        self.assertFalse(result)

    def test_login_inactive_user(self):
        serializer = LoginSerializer(
            data={'username': 'InactiveUser', 'password': 'SomePassword'})
        result = serializer.is_valid()
        self.assertFalse(result)


class UserSerializerTests(TestCase):

    def setUp(self):
        reg_serializer = RegistrationSerializer(data={
            'username': 'SomeUser',
            'password': 'SomePassword'
        })
        result = reg_serializer.is_valid()
        self.assertEqual(result, True)
        self.user = reg_serializer.save()

    def test_user_partial_update(self):
        serializer = UserSerializer(
            self.user, data={'email': 'someuser@mail.com'}, partial=True)
        result = serializer.is_valid()
        self.assertEqual(result, True)
        serializer.save()
        self.assertEqual(self.user.email, 'someuser@mail.com')

    def test_update_require_all_data(self):
        serializer = UserSerializer(
            self.user, data={'email': 'someuser@mail.com'})
        result = serializer.is_valid()
        self.assertEqual(result, False)
        serializer = UserSerializer(self.user, data={
            'email': 'someuser@mail.com',
            'password': 'NewPassword'
        })
        result = serializer.is_valid()
        self.assertEqual(result, True)

    def test_changes_in_profile(self):
        serializer = UserSerializer(self.user, data={
            'email': 'someuser@mail.com',
            'about': 'my about',
            'pic': 'https://my.pic.com/my.png',
            'password': 'NewPassword'
        })
        result = serializer.is_valid()
        serializer.save()
        self.assertEqual(result, True)
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
