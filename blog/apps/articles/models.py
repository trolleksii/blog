from django.db import models

from apps.core.models import TimeStampedModel

from apps.profiles.models import Profile


class Tag(models.Model):
    slug = models.SlugField(db_index=True, max_length=50, unique=True)
    body = models.TextField(max_length=50, unique=True)

    def __str__(self):
        return self.body


class Article(TimeStampedModel):
    slug = models.SlugField(db_index=True, max_length=128, unique=True)
    title = models.CharField(max_length=128)
    body = models.TextField(max_length=1000)
    author = models.ForeignKey(Profile, related_name='articles', on_delete=models.CASCADE)
    liked_by = models.ManyToManyField(Profile, related_name='liked_articles')
    disliked_by = models.ManyToManyField(Profile, related_name='disliked_articles')
    tags = models.ManyToManyField(Tag, related_name='articles')

    def __str__(self):
        return self.title

    def get_likes(self):
        return self.liked_by.count()

    def get_dislikes(self):
        return self.disliked_by.count()


class Comment(TimeStampedModel):
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=500)
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, related_name='comemnts', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
