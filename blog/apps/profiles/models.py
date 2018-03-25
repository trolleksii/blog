from django.db import models

from apps.authentication.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=500)
    pic = models.URLField(blank=True)

    def __str__(self):
        return self.user.username
