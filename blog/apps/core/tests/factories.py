import factory

from apps.posts.models import Comment, Post, Tag
from apps.profiles.models import Profile
from apps.authentication.models import User
from apps.core.text import unique_slugify


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda x: 'user{}'.format(x))
    password = 'qwerty123'
    email = factory.Faker('email')


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    about = factory.Faker('sentence', nb_words=4)
    pic = "http://sourse.somedomain.com/some_pic.png"


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(ProfileFactory)
    body = factory.Faker('sentence', nb_words=4)
    title = factory.Sequence(lambda x: 'Post Title {}'.format(x))
    slug = factory.LazyAttribute(lambda x: unique_slugify(model=Post, text=x.title))


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    title = factory.Sequence(lambda x: 'Comment Title {}'.format(x))
    body = factory.Faker('sentence', nb_words=4)


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    body = factory.Sequence(lambda x: 'tag{}'.format(x))
    slug = factory.LazyAttribute(lambda x: unique_slugify(model=Tag, text=x.body))
