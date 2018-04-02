from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.authentication.models import User
from apps.profiles.models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    user = kwargs.get('instance', None)
    if not Profile.objects.filter(user=user).exists():
        Profile.objects.create(user=user)
