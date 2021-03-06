from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.posts.models import Post, Comment, Tag

from apps.profiles.models import Profile


class PostModelTests(TestCase):

    fixtures = ['posts.json']

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
        post = Post.objects.first()
        duplicate_post = Post(
            title='some other title',
            slug=post.slug,
            body='post body',
            author=author
        )
        with self.assertRaises(ValidationError):
            duplicate_post.full_clean()

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

    fixtures = ['posts.json']

    def test_str(self):
        comment = Comment.objects.first()
        self.assertIsNotNone(comment)
        self.assertEqual(str(comment), comment.title)

    def test_commens_deleted_with_post_delete(self):
        post = Post.objects.first()
        comments_pks = [value['pk'] for value in post.comments.values('pk')]
        self.assertNotEqual(len(comments_pks), 0)
        post.delete()
        for pk in comments_pks:
            self.assertFalse(Comment.objects.filter(pk=pk).exists())


class TagModelTests(TestCase):

    def test_str(self):
        tag = Tag.objects.create(
            body='New Tag'
        )
        self.assertEqual(str(tag), tag.body)

    def test_add_duplicate_tag(self):
        Tag.objects.create(
            body='New Tag'
        )
        duplicate = Tag(
            body='New Tag'
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
