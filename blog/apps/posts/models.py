from django.db import models

from apps.core.models import TimeStampedModel


class Tag(models.Model):
    body = models.TextField(db_index=True, max_length=50, unique=True, blank=False)

    def __str__(self):
        return self.body


class Post(TimeStampedModel):
    slug = models.SlugField(db_index=True, max_length=128, unique=True, blank=False)
    title = models.CharField(max_length=128, blank=False)
    body = models.TextField(max_length=1000, blank=False)
    author = models.ForeignKey('profiles.Profile', related_name='posts', on_delete=models.CASCADE)
    tags = models.ManyToManyField('posts.Tag', related_name='posts')

    def __str__(self):
        return self.title

    def get_likes(self):
        return self.liked_by.count()

    def get_dislikes(self):
        return self.disliked_by.count()


class Comment(TimeStampedModel):
    title = models.CharField(max_length=100, blank=False)
    body = models.TextField(max_length=500, blank=False)
    post = models.ForeignKey('posts.Post', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey('profiles.Profile', related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
