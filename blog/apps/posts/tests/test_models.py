from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.posts.models import Post, Comment, Tag

from apps.profiles.models import Profile


class PostModelTests(TestCase):

    fixtures = ['db.json']

    def test_create_empty_title(self):
        author = Profile.objects.get(user__username='kenny')
        post = Post(
            title='',
            slug='second-post',
            body='post body',
            author=author
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_empty_slug(self):
        author = Profile.objects.get(user__username='kenny')
        post = Post(
            title='Second post',
            slug='',
            body='post body',
            author=author
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_empty_body(self):
        author = Profile.objects.get(user__username='kenny')
        post = Post(
            title='Second post',
            slug='second-post',
            body='',
            author=author
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_no_author(self):
        post = Post(
            title='Second post',
            slug='second-post',
            body='post body',
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_duplicate_slug_post(self):
        author = Profile.objects.get(user__username='kenny')
        post = Post(
            title='some title',
            slug='my-very-first-post',
            body='post body',
            author=author
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_str(self):
        author = Profile.objects.get(user__username='kenny')
        post = Post.objects.create(
            slug='the-first-post',
            title='The first post',
            body='blah blah blah...',
            author=author
        )
        self.assertEqual(str(post), post.title)


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
