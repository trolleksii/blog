from django.shortcuts import reverse
from django.test import TestCase

from apps.posts.models import Tag


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
