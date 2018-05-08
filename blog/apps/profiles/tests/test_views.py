from django.shortcuts import reverse
from django.test import TestCase

from rest_framework import status

from apps.authentication.models import User


class ProfilesTests(TestCase):

    VIEWNAME = ''
    CONTENT_TYPE = 'application/json'
    TOKEN_PREFIX = 'Bearer'
    TEST_USERS = {}

    def setUp(self):
        for user in self.TEST_USERS:
            User.objects.create_user(**user)

    def get_headers(self, *, token, **kwargs):
        return {'HTTP_AUTHORIZATION': ' '.join((self.TOKEN_PREFIX, token))}

    def get_request_path(self, reverse_viewname=None, reverse_kwargs={}):
        _viewname = reverse_viewname or self.VIEWNAME
        self.assertTrue(_viewname, msg='You must specify either reverse_viewname'
                        'or set .VIEWNAME attribute on the view')
        return reverse(_viewname, kwargs=reverse_kwargs)


class ProfileViewTests(ProfilesTests):

    VIEWNAME = 'profiles:profile_view'
    TEST_USERS = [
        {'username': 'kenny', 'password': 'qwerty123'},
        {'username': 'stan', 'password': 'qwerty123'}
    ]

    def setUp(self):
        super().setUp()
        follower = User.objects.get(username=self.TEST_USERS[0]['username']).profile
        followee = User.objects.get(username=self.TEST_USERS[1]['username']).profile
        follower.follow(followee)

    def test_get_profile_info(self):
        token = User.objects.get(username='kenny').token
        response = self.client.get(
            self.get_request_path(reverse_kwargs={'username': 'stan'}),
            **self.get_headers(token=token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = response.data.get('profile', None)
        self.assertEqual(profile['username'], 'stan')
        self.assertTrue(profile['following'])

    def test_get_profile_info_unauthenticated(self):
        response = self.client.get(
            self.get_request_path(reverse_kwargs={'username': 'stan'}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = response.data.get('profile', None)
        self.assertEqual(profile['username'], 'stan')
        self.assertFalse(profile['following'])


class ProfileFollowViewTests(ProfilesTests):

    VIEWNAME = 'profiles:follow_view'
    TEST_USERS = [
        {'username': 'kenny', 'password': 'qwerty123'},
        {'username': 'kyle', 'password': 'qwerty123'}
    ]

    def test_follow_self(self):
        token = User.objects.get(username='kyle').token
        response = self.client.post(
            self.get_request_path(reverse_kwargs={'username': 'kyle'}),
            **self.get_headers(token=token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('profile', {})
        self.assertFalse(data.get('following', True))

    def test_follow_profile(self):
        token = User.objects.get(username='kenny').token
        response = self.client.post(
            self.get_request_path(reverse_kwargs={'username': 'kyle'}),
            **self.get_headers(token=token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('profile', None)
        self.assertTrue(data['following'])

    def test_unfollow(self):
        follower = User.objects.get(username='kenny')
        followee = User.objects.get(username='kyle')
        follower.profile.follow(followee.profile)
        self.assertTrue(follower.profile.has_in_followees(followee))
        response = self.client.delete(
            self.get_request_path(reverse_kwargs={'username': followee}),
            **self.get_headers(token=follower.token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('profile', None)
        self.assertFalse(data['following'])

    def test_unauthenticated(self):
        response = self.client.post(
            self.get_request_path(reverse_kwargs={'username': 'kyle'}),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileFolloweesViewTests(ProfilesTests):

    VIEWNAME = 'profiles:followees_view'
    TEST_USERS = [
        {'username': 'kenny', 'password': 'qwerty123'},
        {'username': 'stan', 'password': 'qwerty123'},
        {'username': 'kyle', 'password': 'qwerty123'}
    ]

    def setUp(self):
        super().setUp()
        self.followees = []
        self.follower = User.objects.get(username=self.TEST_USERS[0]['username']).profile
        for entry in self.TEST_USERS[1:]:
            followee = User.objects.get(username=entry['username']).profile
            self.follower.follow(followee)
            self.followees.append(entry['username'])

    def test_get_followees_if_absent(self):
        token = User.objects.get(username='stan').token
        response = self.client.get(
            self.get_request_path(),
            **self.get_headers(token=token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        followees = response.data.get('followees', None)
        self.assertEqual(followees, [])

    def test_get_followees(self):
        token = User.objects.get(username='kenny').token
        response = self.client.get(
            self.get_request_path(),
            **self.get_headers(token=token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        followees = response.data.get('followees', None)
        self.assertEqual(set(followees), set(self.followees))

    def test_get_unauthenticated(self):
        response = self.client.get(
            self.get_request_path()
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
