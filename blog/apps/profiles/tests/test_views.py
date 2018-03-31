from django.shortcuts import reverse
from django.test import TestCase

from apps.authentication.models import User


class ProfileViewTests(TestCase):

    fixtures = ['profiles.json']

    def test_get_profile_info(self):
        # Kenny makes request to see Stan's profile
        token = User.objects.get(username='kenny').token
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + token
        }
        response = self.client.get(
            reverse('profiles:profile_view', kwargs={'username': 'stan'}),
            **headers
        )
        profile = response.data.get('profile', None)
        self.assertEqual(profile['username'], 'stan')
        self.assertTrue(profile['following'])

    def test_get_profile_info_unauthenticated(self):
        response = self.client.get(
            reverse('profiles:profile_view', kwargs={'username': 'stan'})
        )
        profile = response.data.get('profile', None)
        self.assertEqual(profile['username'], 'stan')
        self.assertFalse(profile['following'])


class ProfileFollowViewTests(TestCase):

    fixtures = ['profiles.json']

    def test_follow_self(self):
        token = User.objects.get(username='kyle').token
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + token
        }
        response = self.client.post(
            reverse('profiles:follow_view', kwargs={'username': 'kyle'}),
            data={},
            content_type='application/json',
            **headers
        )
        data = response.data.get('profile', None)
        self.assertFalse(data['following'])

    def test_follow_profile(self):
        token = User.objects.get(username='kenny').token
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + token
        }
        response = self.client.post(
            reverse('profiles:follow_view', kwargs={'username': 'kyle'}),
            data={},
            content_type='application/json',
            **headers
        )
        data = response.data.get('profile', None)
        self.assertTrue(data['following'])

    def test_unfollow(self):
        user = User.objects.get(username='kenny')
        followee = 'kyle'
        user_has_followee = len(user.profile.followees.filter(
            user__username=followee)) == 1
        self.assertTrue(user_has_followee)
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + user.token
        }
        response = self.client.delete(
            reverse('profiles:follow_view', kwargs={'username': followee}),
            data={},
            content_type='application/json',
            **headers
        )
        data = response.data.get('profile', None)
        self.assertFalse(data['following'])

    def test_unauthenticated(self):
        response = self.client.post(
            reverse('profiles:follow_view', kwargs={'username': 'kyle'}),
            data={},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)


class ProfileFolloweesViewTests(TestCase):

    fixtures = ['profiles.json']

    def test_get_empty_follows(self):
        token = User.objects.get(username='stan').token
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + token
        }
        response = self.client.get(
            reverse('profiles:followees_view'),
            **headers
        )
        followees = response.data.get('followees', None)
        self.assertEqual(followees, [])

    def test_get_follows(self):
        token = User.objects.get(username='kenny').token
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + token
        }
        response = self.client.get(
            reverse('profiles:followees_view'),
            **headers
        )
        followees = response.data.get('followees', None)
        self.assertEqual(set(followees), set(['stan', 'kyle']))

    def test_get_unauthenticated(self):
        response = self.client.get(
            reverse('profiles:followees_view'),
        )
        self.assertEqual(response.status_code, 403)
