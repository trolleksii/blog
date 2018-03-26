from django.test import TestCase

from apps.articles.models import Article, Comment, Tag

from apps.profiles.models import Profile, User


class ArticleModelTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username='kenny',
            password='qwerty123',
            email='kenny@spmail.com'
        )
        self.profile = Profile.objects.create(
            user=user,
            about='I am Kenny',
            pic='http://static.domain.com/images/kenny.png'
        )

    def test_str(self):
        article = Article.objects.create(
            slug='the-first-article',
            title='The first article',
            body='blah blah blah...',
            author=self.profile
        )
        self.assertEqual(str(article), article.title)


class CommentModelTests(TestCase):

    def test_str(self):
        pass


class TagModelTests(TestCase):

    def test_str(self):
        tag = Tag.objects.create(
            slug='new-tag',
            body='New Tag'
        )
        self.assertEqual(str(tag), tag.body)
