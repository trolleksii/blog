import factory

from apps.authentication.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    password = 'qwerty123'
    email = factory.Faker('email')


class PostFactory(factory.django.DjangoModelFactory):
    pass


class CommentFactory(factory.django.DjangoModelFactory):
    pass
