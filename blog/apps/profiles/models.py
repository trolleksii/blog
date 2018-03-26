from django.db import models

from apps.authentication.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=500)
    pic = models.URLField(blank=True)
    followees = models.ManyToManyField('self', related_name='followers', symmetrical=False)

    def __str__(self):
        return self.user.username

    def follow(self, profile):
        if profile is not self:
            self.followees.add(profile)

    def unfollow(self, profile):
        if profile is not self:
            self.followees.remove(profile)

    # follower --> me --> followee
    def has_in_followees(self, profile):
        if profile is not self:
            return self.followees.filter(pk=profile.pk).exists()
        return False

    # def is_in_followers(self, profile):
    #     return self.followers.filter(pk=profile.pk).exists()
