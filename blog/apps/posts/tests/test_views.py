import json
import random

from django.shortcuts import reverse
from django.test import TestCase

from rest_framework import status

from apps.authentication.models import User
from apps.core.tests.factories import PostFactory, TagFactory, UserFactory
from apps.posts.models import Comment, Post, Tag
from apps.posts.pagination import PostsPaginaton


class TagViewTests(TestCase):

    fixtures = ['posts.json']

    def test_list_available_tags(self):
        tags = Tag.objects.values('body')
        tags_list = {tag['body'] for tag in tags}
        response = self.client.get(reverse('posts:listtags_view'))
        data = set(response.data.get('tagList'))
        self.assertEqual(tags_list, data)


class PostViewSetTests(TestCase):

    users_num = 4
    posts_num = 30

    def setUp(self):
        self.users = []
        self.tags = []
        for x in range(self.users_num):
            user = UserFactory()
            user.save()
            if len(self.users) > 1:
                user.profile.follow(random.choice(self.users).profile)
            self.users.append(user)
            tag = TagFactory()
            tag.save()
            self.tags.append(tag)
        for i in range(self.posts_num):
            post = PostFactory(author=random.choice(self.users).profile)
            post.tags.add(random.choice(self.tags))
            post.save()
            random.choice(self.users).profile.favorite(post)

    def test_list_posts(self):
        posts_count = Post.objects.count()
        response = self.client.get(
            reverse('posts:post-list'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['postsCount'], posts_count)
        page_len = PostsPaginaton.default_limit
        self.assertLessEqual(len(response.data['posts']), page_len)

    def test_list_posts_by_tag(self):
        tag = self.tags[0]
        response = self.client.get(
            reverse('posts:post-list') + '?tag={}'.format(tag),
            content_type='application/json'
        )
        total_posts = Post.objects.filter(tags__body=tag).count()
        self.assertEqual(response.data['postsCount'], total_posts)
        for entry in response.data['posts']:
            self.assertEqual([tag.body], entry['tagList'])

    def test_list_posts_favorited_by_person(self):
        user = self.users[0]
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.get(
            reverse('posts:post-list') + '?favorited={}'.format(user),
            content_type='application/json',
            **headers
        )
        total_posts = Post.objects.filter(favorited_by=user.profile).count()
        self.assertEqual(response.data['postsCount'], total_posts)
        for entry in response.data['posts']:
            self.assertTrue(entry['favorited'])

    def test_list_posts_by_author(self):
        author = self.users[0].profile
        response = self.client.get(
            reverse('posts:post-list') + '?author={}'.format(author),
            content_type='application/json'
        )
        total_posts = Post.objects.filter(author=author).count()
        self.assertEqual(response.data['postsCount'], total_posts)
        for entry in response.data['posts']:
            self.assertEqual(author.user.username, entry['author']['username'])

    def test_list_pagination(self):
        posts_count = Post.objects.count()
        limit = 10
        offset = posts_count // 3
        response = self.client.get(
            reverse('posts:post-list') + '?limit={}&offset={}'.format(limit, offset),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['postsCount'], posts_count)
        self.assertLessEqual(len(response.data['posts']), limit)
        self.assertEqual(
            response.data['posts'][0]['title'],
            Post.objects.all().order_by('-created_at', '-modified_at')[offset].title
        )

    def test_feed(self):
        user = self.users[0]
        posts_count = Post.objects.filter(author__in=user.profile.followees.all()).count()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.get(
            reverse('posts:post-feed'),
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['postsCount'], posts_count)

    def test_retrieve_post(self):
        post = Post.objects.first()
        response = self.client.get(
            reverse('posts:post-detail', kwargs={'slug': post.slug}),
            content_type='application/json'
        )
        data = response.data['post']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['title'], post.title)

    def test_retrieve_post_wrong_slug(self):
        response = self.client.get(
            reverse('posts:post-detail', kwargs={'slug': 'mock slug'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_post(self):
        user = User.objects.last()
        data = {
            'title': 'mock post',
            'body': 'body of a mock post',
            'tagList': ['mock', 'fake']
        }
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.post(
            reverse('posts:post-list'),
            data=json.dumps({'post': data}),
            content_type='application/json',
            **headers
        )
        response_data = response.data['post']
        tags = data.pop('tagList')
        post = Post.objects.get(title=data['title'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tags), post.tags.count())
        for key, value in data.items():
            self.assertEqual(value, response_data[key])
            self.assertEqual(value, getattr(post, key))

    def test_create_post_unauth(self):
        data = {
            'title': 'mock post',
            'body': 'body of a mock post',
            'tagList': ['mock', 'fake']
        }
        response = self.client.post(
            reverse('posts:post-list'),
            data=json.dumps({'post': data}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_own_post(self):
        user = User.objects.first()
        post = user.profile.posts.first()
        self.assertIsNotNone(post)
        data = {
            'title': 'mock post',
            'body': 'body of a mock post',
            'tagList': ['mock', 'fake']
        }
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.put(
            reverse('posts:post-detail', kwargs={'slug': post.slug}),
            data=json.dumps({'post': data}),
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_own_post_no_data(self):
        user = User.objects.first()
        post = user.profile.posts.first()
        self.assertIsNotNone(post)
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.put(
            reverse('posts:post-detail', kwargs={'slug': post.slug}),
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_anothers_post(self):
        owner = User.objects.first()
        post = owner.profile.posts.first()
        self.assertIsNotNone(post)
        modifier = User.objects.last()
        self.assertNotEqual(owner, modifier)
        data = {
            'title': 'mock post',
            'body': 'body of a mock post',
            'tagList': ['mock', 'fake']
        }
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + modifier.token
        }
        response = self.client.put(
            reverse('posts:post-detail', kwargs={'slug': post.slug}),
            data=json.dumps({'post': data}),
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_post_unauth(self):
        user = User.objects.first()
        post = user.profile.posts.first()
        self.assertIsNotNone(post)
        data = {
            'title': 'mock post',
            'body': 'body of a mock post',
            'tagList': ['mock', 'fake']
        }
        response = self.client.put(
            reverse('posts:post-detail', kwargs={'slug': post.slug}),
            data=json.dumps({'post': data}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_own_post(self):
        user = User.objects.first()
        post = user.profile.posts.first()
        self.assertIsNotNone(post)
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.delete(
            reverse('posts:post-detail', kwargs={'slug': post.slug}),
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_delete_anothers_post(self):
        owner = User.objects.first()
        post = owner.profile.posts.first()
        self.assertIsNotNone(post)
        modifier = User.objects.last()
        self.assertNotEqual(owner, modifier)
        data = {
            'title': 'mock post',
            'body': 'body of a mock post',
            'tagList': ['mock', 'fake']
        }
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + modifier.token
        }
        response = self.client.delete(
            reverse('posts:post-detail', kwargs={'slug': post.slug}),
            data=json.dumps({'post': data}),
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_unauth(self):
        user = User.objects.first()
        post = user.profile.posts.first()
        self.assertIsNotNone(post)
        response = self.client.delete(
            reverse('posts:post-detail', kwargs={'slug': post.slug}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_favorite_post(self):
        profile = User.objects.first().profile
        post = profile.posts.first()
        # in case if setUp favourited this post with this profile
        profile.unfavorite(post)
        self.assertIsNotNone(post)
        self.assertNotIn(post, profile.favorites.all())
        favorites_before = profile.favorites.count()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + profile.user.token
        }
        response = self.client.post(
            reverse('posts:post-favorite', kwargs={'slug': post.slug}),
            **headers
        )
        favorites_after = profile.favorites.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(favorites_after - favorites_before, 1)

    def test_favorite_wrong_slug(self):
        user = User.objects.first()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.post(
            reverse('posts:post-favorite', kwargs={'slug': 'wrong slug'}),
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_favorite_unauth(self):
        post = Post.objects.first()
        response = self.client.post(
            reverse('posts:post-favorite', kwargs={'slug': post.slug}),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unfavorite_post(self):
        post = Post.objects.first()
        user = User.objects.last()
        user.profile.favorite(post)
        self.assertIsNotNone(post)
        self.assertIn(post, user.profile.favorites.all())
        favorites_before = user.profile.favorites.count()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.delete(
            reverse('posts:post-favorite', kwargs={'slug': post.slug}),
            **headers
        )
        favorites_after = user.profile.favorites.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(favorites_before - favorites_after, 1)

    def test_unfavorite_wrong_slug(self):
        user = User.objects.first()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.delete(
            reverse('posts:post-favorite', kwargs={'slug': 'wrong slug'}),
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfavorite_unauth(self):
        post = Post.objects.first()
        response = self.client.delete(
            reverse('posts:post-favorite', kwargs={'slug': post.slug}),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_post(self):
        post = User.objects.first().profile.posts.first()
        voter = User.objects.last()
        self.assertIsNotNone(post)
        self.assertNotIn(post, voter.profile.liked_posts.all())
        likes_before = post.get_likes()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + voter.token
        }
        response = self.client.post(
            reverse('posts:post-like', kwargs={'slug': post.slug}),
            **headers
        )
        likes_after = post.get_likes()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(likes_after - likes_before, 1)

    def test_like_post_unauth(self):
        post = Post.objects.first()
        response = self.client.post(
            reverse('posts:post-like', kwargs={'slug': post.slug}),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_wrong_slug(self):
        user = User.objects.first()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.post(
            reverse('posts:post-like', kwargs={'slug': 'wrong slug'}),
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_dislike_post(self):
        post = User.objects.first().profile.posts.first()
        voter = User.objects.last()
        self.assertIsNotNone(post)
        self.assertNotIn(post, voter.profile.disliked_posts.all())
        dislikes_before = post.get_dislikes()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + voter.token
        }
        response = self.client.delete(
            reverse('posts:post-like', kwargs={'slug': post.slug}),
            **headers
        )
        dislikes_after = post.get_dislikes()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dislikes_after - dislikes_before, 1)

    def test_dislike_post_unauth(self):
        post = Post.objects.first()
        response = self.client.delete(
            reverse('posts:post-like', kwargs={'slug': post.slug}),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dislike_wrong_slug(self):
        user = User.objects.first()
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.delete(
            reverse('posts:post-like', kwargs={'slug': 'wrong slug'}),
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentCreateListViewTests(TestCase):

    fixtures = ['posts.json']

    def test_create_comment(self):
        post = Post.objects.first()
        user = User.objects.first()
        comment = {
            'title': 'comment from tests',
            'body': 'body of the comment created from tests'
        }
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.post(
            reverse('posts:comments_view', kwargs={'slug': post.slug}),
            data=json.dumps({'comment': comment}),
            content_type='application/json',
            **headers
        )
        data = response.data['comment']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['title'], comment['title'])
        self.assertEqual(data['body'], comment['body'])
        self.assertEqual(data['author']['username'], user.username)
        self.assertTrue(
            post.comments.filter(pk=data['id']).exists()
        )

    def test_create_comment_wrong_slug(self):
        user = User.objects.first()
        comment = {
            'title': 'comment from tests',
            'body': 'body of the comment created from tests'
        }
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + user.token
        }
        response = self.client.post(
            reverse('posts:comments_view', kwargs={'slug': 'mock slug'}),
            data=json.dumps({'comment': comment}),
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_comment_unauthorized(self):
        post = Post.objects.first()
        comment = {
            'title': 'comment from tests',
            'body': 'body of the comment created from tests'
        }
        response = self.client.post(
            reverse('posts:comments_view', kwargs={'slug': post.slug}),
            data=json.dumps({'comment': comment}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_comments(self):
        post = Post.objects.first()
        response = self.client.get(
            reverse('posts:comments_view', kwargs={'slug': post.slug}),
            content_type='application/json'
        )
        comments = response.data['comments']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(comments), post.comments.count())

    def test_list_comments_wrong_slug(self):
        response = self.client.get(
            reverse('posts:comments_view', kwargs={'slug': 'mock slug'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentDestroyViewTests(TestCase):

    fixtures = ['posts.json']

    def test_delete_own_comment(self):
        post_author = User.objects.get(username='kenny')
        comment = post_author.profile.comments.first()
        slug = comment.post.slug
        pk = comment.pk
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + post_author.token
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNotNone(response.data.get('errors', None))

    def test_delete_someones_comment(self):
        post_author = User.objects.get(username='kenny')
        token = User.objects.get(username='kyle').token
        comment = post_author.profile.comments.first()
        slug = comment.post.slug
        pk = comment.pk
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + token
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Comment.objects.filter(pk=pk).exists()
        )
