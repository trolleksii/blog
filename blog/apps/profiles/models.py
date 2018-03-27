from django.db import models

from apps.authentication.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=500)
    pic = models.URLField(blank=True)
    followees = models.ManyToManyField('self', related_name='followers', symmetrical=False)
    favorites = models.ManyToManyField('posts.Post', related_name='favorited_by')

    def __str__(self):
        return self.user.username

    def favorite(self, post):
        self.favorites.add(post)

    def follow(self, profile):
        if profile != self:
            self.followees.add(profile)

    def unfavorite(self, post):
        self.favorites.remove(post)

    def unfollow(self, profile):
        if profile != self:
            self.followees.remove(profile)

    def has_in_favorites(self, post):
        return self.favorites.filter(pk=post.pk).exists()

    # follower --> me --> followee
    def has_in_followees(self, profile):
        if profile is not self:
            return self.followees.filter(pk=profile.pk).exists()
        return False

    # def is_in_followers(self, profile):
    #     return self.followers.filter(pk=profile.pk).exists()
