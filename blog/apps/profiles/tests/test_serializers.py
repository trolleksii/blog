from django.test import TestCase

from apps.profiles.models import Profile
from apps.profiles.serializers import ProfileFolloweesSerializer, ProfileSerializer


class ProfileSerializerTests(TestCase):

    fixtures = ['profiles.json']

    def test_get_profile_info_follows(self):
        follower = Profile.objects.get(user__username='kenny')
        followee = Profile.objects.get(user__username='kyle')
        serializer = ProfileSerializer(followee, context={'user': follower.user})
        self.assertEqual(serializer.data['username'], followee.user.username)
        self.assertEqual(serializer.data['about'], followee.about)
        self.assertEqual(serializer.data['pic'], followee.pic)
        self.assertTrue(serializer.data['following'])

    def test_get_profile_info_not_follows(self):
        follower = Profile.objects.get(user__username='kyle')
        followee = Profile.objects.get(user__username='kenny')
        serializer = ProfileSerializer(followee, context={'user': follower.user})
        self.assertEqual(serializer.data['username'], followee.user.username)
        self.assertEqual(serializer.data['about'], followee.about)
        self.assertEqual(serializer.data['pic'], followee.pic)
        self.assertFalse(serializer.data['following'])


class ProfileFolloweesSerializerTests(TestCase):

    fixtures = ['profiles.json']

    def test_get_followees(self):
        profile = Profile.objects.get(user__username='kenny')
        serializer = ProfileFolloweesSerializer(profile)
        expected_list = ['kyle', 'stan']
        self.assertEqual(set(expected_list), set(serializer.data['followees']))

    def test_get_no_followees(self):
        profile = Profile.objects.get(user__username='kyle')
        serializer = ProfileFolloweesSerializer(profile)
        expected_list = []
        self.assertEqual(expected_list, serializer.data['followees'])
