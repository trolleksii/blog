from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.authentication.models import User
from apps.profiles.models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, **kwargs):
    user_created = kwargs.get('created', False)
    if user_created:
        Profile.objects.create(user=instance)
