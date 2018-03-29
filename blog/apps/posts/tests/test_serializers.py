from django.test import TestCase

from apps.authentication.models import User
from apps.posts.models import Comment, Post, Tag
from apps.posts.serializers import CommentSerializer, PostSerializer, TagSerializer


class CommentSerializerTests(TestCase):

    fixtures = ['db.json']

    def test_serialize_comment(self):
        comment = Comment.objects.first()
        serializer = CommentSerializer(comment)
        data = serializer.data
        self.assertEqual(data['id'], comment.pk)
        self.assertEqual(data['title'], comment.title)
        self.assertEqual(data['body'], comment.body)
        self.assertEqual(data['author']['username'], comment.author.user.username)

    def test_serialize_multiple_comments(self):
        qset = Comment.objects.all()
        comment = qset.first()
        qset_serializer = CommentSerializer(qset, many=True)
        comment_serializer = CommentSerializer(comment)
        qset_data = qset_serializer.data
        comment_data = comment_serializer.data
        self.assertEqual(qset.count(), len(qset_data))
        self.assertEqual(comment_data, qset_data[0])

    def test_deserialize_comment(self):
        user = User.objects.get(username='eric')
        post = Post.objects.first()
        data = {
            'title': 'Test comment by eric',
            'body': 'blah blah blah'
        }
        serializer = CommentSerializer(
            data=data,
            context={'user': user, 'post': post}
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        comment = Comment.objects.get(title=data['title'])
        self.assertEqual(comment.body, data['body'])
        self.assertEqual(comment.post.pk, post.pk)
        self.assertEqual(comment.author.pk, user.profile.pk)

    def test_deserialize_comment_without_post(self):
        user = User.objects.get(username='eric')
        data = {
            'title': 'Test comment by eric',
            'body': 'blah blah blah'
        }
        serializer = CommentSerializer(data=data, context={'user': user})
        self.assertFalse(serializer.is_valid())

    def test_deserialize_comment_without_author(self):
        post = Post.objects.first().pk
        data = {
            'title': 'Test comment by eric',
            'body': 'blah blah blah'
        }
        serializer = CommentSerializer(data=data, context={'post': post})
        self.assertFalse(serializer.is_valid())

    def test_deserialize_empty_title(self):
        user = User.objects.get(username='eric')
        post = Post.objects.first().pk
        data = {
            'title': '',
            'body': 'blah blah blah'
        }
        serializer = CommentSerializer(
            data=data,
            context={'user': user, 'post': post}
        )
        self.assertFalse(serializer.is_valid())

    def test_deserialize_empty_body(self):
        user = User.objects.get(username='eric')
        post = Post.objects.first().pk
        data = {
            'title': 'Test comment by eric',
            'body': ''
        }
        serializer = CommentSerializer(
            data=data,
            context={'user': user, 'post': post}
        )
        self.assertFalse(serializer.is_valid())


class PostSerializerTests(TestCase):

    fixtures = ['db.json']

    def test_serialize_post(self):
        post = Post.objects.first()
        serializer = PostSerializer(post)
        data = serializer.data
        self.assertEqual(post.slug, data['slug'])
        self.assertEqual(post.title, data['title'])
        self.assertEqual(post.body, data['body'])
        self.assertEqual(post.author.user.username, data['author']['username'])
        self.assertEqual(post.get_likes(), data['likes'])
        self.assertEqual(post.get_dislikes(), data['dislikes'])
        self.assertEqual(post.tags.count(), len(data['tagList']))

    def test_serialize_multiple_posts(self):
        # if test_serialize_post is working fine, there is no need to check
        # every field of every entry, just total count and the first entry
        queryset = Post.objects.all()
        one_post = queryset.first()
        qset_serializer = PostSerializer(queryset, many=True)
        onepost_serializer = PostSerializer(one_post)
        qset_data = qset_serializer.data
        post_data = onepost_serializer.data
        self.assertEqual(len(qset_data), queryset.count())
        self.assertEqual(post_data, qset_data[0])

    def test_deserialize_with_tags(self):
        user = User.objects.get(username='kenny')
        tags_list = ['sometag1', 'sometag2', 'sometag3']
        serializer = PostSerializer(
            data={
                'tagList': tags_list,
                'title': 'Some random title',
                'body': 'Here goes post body',
            },
            context={'user': user}
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        post = Post.objects.get(title='Some random title')
        self.assertEqual(post.tags.count(), 3)
        tags_qset = Tag.objects.filter(body__in=tags_list)
        for tag in tags_qset:
            self.assertIn(tag, post.tags.all())

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
