from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.articles.models import Article, Comment, Tag

from apps.profiles.models import Profile


class ArticleModelTests(TestCase):

    fixtures = ['db.json']

    def test_create_empty_title(self):
        author = Profile.objects.get(user__username='kenny')
        article = Article(
            title='',
            slug='second-article',
            body='article body',
            author=author
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_create_empty_slug(self):
        author = Profile.objects.get(user__username='kenny')
        article = Article(
            title='Second article',
            slug='',
            body='article body',
            author=author
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_create_empty_body(self):
        author = Profile.objects.get(user__username='kenny')
        article = Article(
            title='Second article',
            slug='second-article',
            body='',
            author=author
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_create_no_author(self):
        article = Article(
            title='Second article',
            slug='second-article',
            body='article body',
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_create_duplicate_slug_article(self):
        author = Profile.objects.get(user__username='kenny')
        article = Article(
            title='some title',
            slug='my-very-first-article',
            body='article body',
            author=author
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_str(self):
        author = Profile.objects.get(user__username='kenny')
        article = Article.objects.create(
            slug='the-first-article',
            title='The first article',
            body='blah blah blah...',
            author=author
        )
        self.assertEqual(str(article), article.title)


class CommentModelTests(TestCase):

    fixtures = ['db.json']

    def test_str(self):
        comment = Comment.objects.first()
        self.assertIsNotNone(comment)
        self.assertEqual(str(comment), comment.title)


class TagModelTests(TestCase):

    def test_str(self):
        tag = Tag.objects.create(
            slug='new-tag',
            body='New Tag'
        )
        self.assertEqual(str(tag), tag.body)

    def test_add_duplicate_tag(self):
        Tag.objects.create(
            slug='new-tag',
            body='New Tag'
        )
        duplicate_slug = Tag(
            slug='new-tag',
            body='Newest Tag'
        )
        duplicate_body = Tag(
            slug='new-tag',
            body='Newest Tag'
        )
        with self.assertRaises(ValidationError):
            duplicate_slug.full_clean()
        with self.assertRaises(ValidationError):
            duplicate_body.full_clean()
