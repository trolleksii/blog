from django.db import models

from apps.authentication.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=500)
    pic = models.URLField(blank=True)
    followees = models.ManyToManyField('self', related_name='followers', symmetrical=False)
    favorites = models.ManyToManyField('posts.Post', related_name='favorited_by')
    liked_posts = models.ManyToManyField('posts.Post', related_name='liked_by')
    disliked_posts = models.ManyToManyField('posts.Post', related_name='disliked_by')

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

    def has_in_followees(self, profile):
        return self.followees.filter(pk=profile.pk).exists()

    def like(self, post):
        if self.can_vote_for(post):
            self.liked_posts.add(post)

    def dislike(self, post):
        if self.can_vote_for(post):
            self.disliked_posts.add(post)

    def can_vote_for(self, post):
        return all(
            [
                not self.is_author_of(post),
                not self._has_liked_post(post),
                not self._has_disliked_post(post)
            ]
        )

    def _has_liked_post(self, post):
        return self.liked_posts.filter(pk=post.pk).exists()

    def _has_disliked_post(self, post):
        return self.disliked_posts.filter(pk=post.pk).exists()

    def is_author_of(self, post_or_comment):
        return post_or_comment.author == self
