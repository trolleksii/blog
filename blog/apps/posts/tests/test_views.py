from django.shortcuts import reverse
from django.test import TestCase

from apps.authentication.models import User

from apps.posts.models import Comment, Tag


class TagViewTests(TestCase):

    fixtures = ['posts.json']

    def test_list_available_tags(self):
        tags = Tag.objects.values('body')
        tags_list = {tag['body'] for tag in tags}
        response = self.client.get(reverse('posts:listtags_view'))
        data = set(response.data.get('tagList'))
        self.assertEqual(tags_list, data)


class PostViewSetTests(TestCase):
    pass


class CommentCreateListViewTests(TestCase):

    def test_create_comment(self):
        pass

    def test_create_comment_wrong_slug(self):
        pass

    def test_create_comment_unauthorized(self):
        pass

    def test_list_comments(self):
        pass

    def test_list_comments_wrong_slug(self):
        pass


class CommentDestroyViewTests(TestCase):

    fixtures = ['posts.json']

    def test_delete_own_comment(self):
        post_author = User.objects.get(username='kenny')
        comment = post_author.profile.comments.first()
        slug = comment.post.slug
        pk = comment.pk
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + post_author.token
        }
        response = self.client.delete(
            reverse(
                'posts:comments_del_view',
                kwargs={
                    'slug': slug,
                    'pk': pk
                }
            ),
            **headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Comment.objects.filter(pk=pk).exists()
        )

    def test_delete_comment_unauthorized(self):
        post_author = User.objects.get(username='kenny')
        comment = post_author.profile.comments.first()
        slug = comment.post.slug
        pk = comment.pk
        response = self.client.delete(
            reverse(
                'posts:comments_del_view',
                kwargs={
                    'slug': slug,
                    'pk': pk
                }
            ),
        )
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(response.data.get('errors', None))

    def test_delete_someones_comment(self):
        post_author = User.objects.get(username='kenny')
        token = User.objects.get(username='kyle').token
        comment = post_author.profile.comments.first()
        slug = comment.post.slug
        pk = comment.pk
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + token
        }
        response = self.client.delete(
            reverse(
                'posts:comments_del_view',
                kwargs={
                    'slug': slug,
                    'pk': pk
                }
            ),
            **headers
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Comment.objects.filter(pk=pk).exists()
        )
