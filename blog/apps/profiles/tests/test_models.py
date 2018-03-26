from django.test import TestCase

from apps.authentication.models import User
from apps.profiles.models import Profile


class ProfileModelTests(TestCase):

    fixtures = ['db.json']

    def test_str_method(self):
        user = User.objects.get(username='kenny')
        profile = Profile.objects.get(user=user)
        self.assertEqual(str(profile), user.username)

    def test_follow(self):
        profile1 = Profile.objects.get(user__username='eric')
        profile1_followees = profile1.followees.all()
        self.assertEqual(len(profile1_followees), 0)
        profile2 = Profile.objects.get(user__username='kyle')
        profile2_followees = profile2.followees.all()
        self.assertEqual(len(profile2_followees), 0)
        profile1.follow(profile2)
        profile1_followees = profile1.followees.all()
        profile2_followees = profile2.followees.all()
        self.assertEqual(len(profile1_followees), 1)
        self.assertEqual(len(profile2_followees), 0)
        self.assertEqual(profile1.followees.first(), profile2)

    def test_unfollow(self):
        profile1 = Profile.objects.get(user__username='kenny')
        profile2 = Profile.objects.get(user__username='kyle')
        followees_match = profile1.followees.filter(user__username='kyle')
        self.assertEqual(len(followees_match), 1)
        profile1.unfollow(profile2)
        followees_match = profile1.followees.filter(user__username='kyle')
        self.assertEqual(len(followees_match), 0)

    def test_has_in_followees(self):
        profile1 = Profile.objects.get(user__username='kenny')
        profile2 = Profile.objects.get(user__username='kyle')
        self.assertTrue(
            profile1.has_in_followees(profile2)
        )
        self.assertFalse(
            profile2.has_in_followees(profile1)
        )

    def test_follow_yourself(self):
        profile = Profile.objects.get(user__username='kyle')
        profile.follow(profile)
        followees = profile.followees.all()
        self.assertEqual(len(followees), 0)
