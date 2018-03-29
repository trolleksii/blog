from django.test import TestCase

from apps.authentication.models import User
from apps.posts.models import Post, Tag
from apps.posts.serializers import CommentSerializer, PostSerializer, TagSerializer


class CommentSerializerTests(TestCase):

    def test_serialize_comment(self):
        pass

    def test_serialize_multiple_comments(self):
        pass

    def test_deserialize_comment(self):
        pass

    def test_deserialize_comment_without_post(self):
        pass

    def test_deserialize_comment_without_author(self):
        pass

    def test_deserialize_empty_comment(self):
        pass


class PostSerializerTests(TestCase):

    fixtures = ['db.json']

    def test_serialize_post(self):
        post = Post.objects.first()
        serializer = PostSerializer(post)
        self.assertEqual(post.slug, serializer.data['slug'])
        self.assertEqual(post.body, serializer.data['body'])
        self.assertEqual(post.title, serializer.data['title'])
        self.assertEqual(post.author.user.username, serializer.data['author']['username'])

    def test_serialize_multiple_posts(self):
        queryset = Post.objects.all()
        serializer = PostSerializer(queryset, many=True)
        self.assertEqual(len(serializer.data), queryset.count())

    def test_deserialize_with_tags(self):
        user = User.objects.get(username='kenny')
        serializer = PostSerializer(
            data={
                'tagList': ['ctag1', 'ctag2', 'ctag3'],
                'title': 'Some random title',
                'body': 'Here goes post body',
            },
            context={'user': user}
        )
        tags_before = Tag.objects.all().count()
        self.assertTrue(serializer.is_valid())
        serializer.save()
        tags_after = Tag.objects.all().count()
        self.assertEqual(tags_after, tags_before + 3)
        post = Post.objects.get(title='Some random title')
        self.assertEqual(post.tags.count(), 3)

    def test_deserialize_without_tags(self):
        user = User.objects.get(username='kenny')
        serializer = PostSerializer(
            data={
                'title': 'Some random title',
                'body': 'Here goes post body',
            },
            context={'user': user}
        )
        tags_before = Tag.objects.all().count()
        self.assertTrue(serializer.is_valid())
        serializer.save()
        tags_after = Tag.objects.all().count()
        self.assertEqual(tags_after, tags_before)
        post = Post.objects.get(title='Some random title')
        self.assertEqual(post.tags.count(), 0)

    def test_deserialize_without_author(self):
        serializer = PostSerializer(
            data={
                'title': 'Some random title',
                'body': 'Here goes post body',
            },
        )
        self.assertFalse(serializer.is_valid())

    def test_deserialize_empty_body(self):
        user = User.objects.get(username='kenny')
        serializer = PostSerializer(
            data={
                'title': 'Some random title',
                'body': '',
            },
            context={'user': user}
        )
        self.assertFalse(serializer.is_valid())

    def test_deserialize_empty_title(self):
        user = User.objects.get(username='kenny')
        serializer = PostSerializer(
            data={
                'title': '',
                'body': 'Some genius text',
            },
            context={'user': user}
        )
        self.assertFalse(serializer.is_valid())


class TagSerializerTests(TestCase):

    fixtures = ['db.json']

    def test_serialize_tag(self):
        text = 'testtag'
        tag = Tag.objects.create(
            body=text,
            slug=text
        )
        serializer = TagSerializer(tag)
        self.assertEqual(text, serializer.data)

    def test_serialize_multiple_tags(self):
        queryset = Tag.objects.all()
        self.assertGreaterEqual(len(queryset), 2)
        serializer = TagSerializer(queryset, many=True)
        for pos, tag in enumerate(queryset):
            self.assertEqual(tag.body, serializer.data[pos])

    def test_deserialize_tag(self):
        tag_body = 'qwerty'
        serializer = TagSerializer(
            data=tag_body,
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        tags = Tag.objects.filter(body=tag_body)
        self.assertEqual(len(tags), 1)

    def test_deserialize_multiple_tag(self):
        tag_bodys = ['qwerty', 'asdfgh', 'zxcvbn']
        serializer = TagSerializer(
            data=tag_bodys,
            many=True
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        tags = Tag.objects.filter(body__in=tag_bodys)
        self.assertEqual(len(tags), 3)

    def test_deserialize_multiple_tags_with_duplicates(self):
        Tag.objects.create(
            body='asdfgh',
            slug='asdfgh'
        )
        tag_bodys = ['qwerty', 'asdfgh', 'zxcvbn']
        serializer = TagSerializer(
            data=tag_bodys,
            many=True
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        tags = Tag.objects.filter(body__in=tag_bodys)
        self.assertEqual(len(tags), 3)
