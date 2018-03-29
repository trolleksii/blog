from django.test import TestCase

from django.http import HttpRequest

from apps.profiles.models import Profile
from apps.profiles.serializers import ProfileFolloweesSerializer, ProfileSerializer


class ProfileSerializerTests(TestCase):

    fixtures = ['profiles.json']

    def test_get_profile_info_follows(self):
        follower = Profile.objects.get(user__username='kenny')
        followee = Profile.objects.get(user__username='stan')
        request = HttpRequest()
        request.user = follower.user
        serializer = ProfileSerializer(followee, context={'request': request})
        self.assertEqual(serializer.data['username'], followee.user.username)
        self.assertEqual(serializer.data['about'], followee.about)
        self.assertEqual(serializer.data['pic'], followee.pic)
        self.assertTrue(serializer.data['following'])

    def test_get_profile_info_not_follows(self):
        follower = Profile.objects.get(user__username='stan')
        followee = Profile.objects.get(user__username='kenny')
        request = HttpRequest()
        request.user = follower.user
        serializer = ProfileSerializer(followee, context={'request': request})
        self.assertEqual(serializer.data['username'], followee.user.username)
        self.assertEqual(serializer.data['about'], followee.about)
        self.assertEqual(serializer.data['pic'], followee.pic)
        self.assertFalse(serializer.data['following'])


class ProfileFolloweesSerializerTests(TestCase):

    fixtures = ['profiles.json']

    def test_get_followees(self):
        profile = Profile.objects.get(user__username='kenny')
        serializer = ProfileFolloweesSerializer(profile)
        expected_list = ['stan', 'eric', 'kyle']
        self.assertEqual(set(expected_list), set(serializer.data['followees']))

    def test_get_no_followees(self):
        profile = Profile.objects.get(user__username='eric')
        serializer = ProfileFolloweesSerializer(profile)
        expected_list = []
        self.assertEqual(expected_list, serializer.data['followees'])
