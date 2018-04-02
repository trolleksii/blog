from apps.core.factories import UserFactory

from django.test import TestCase


class UserFactoryTests(TestCase):

    def test_user_factory_creates_profile(self):
        user = UserFactory()
        print(user.profile)
