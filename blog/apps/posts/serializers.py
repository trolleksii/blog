from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.text import unique_slugify

from apps.posts.models import Comment, Post, Tag

from apps.profiles.serializers import ProfileSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    class Meta:
        model = Comment
        fields = ['id', 'title', 'body', 'createdAt', 'updatedAt', 'author']
        read_only_fields = ['id']

    def validate(self, args):
        user = self.context.get('user', None)
        if user is None or not user.is_authenticated:
            msg = _('Comment author not set.')
            raise ValidationError(msg)
        post = self.context.get('post', None)
        if post is None:
            msg = _('Post to be commented not set.')
            raise ValidationError(msg)
        args['author'] = user.profile
        args['post'] = post
        return args

    def get_created_at(self, comment):
        return comment.created_at.isoformat()

    def get_updated_at(self, comment):
        return comment.modified_at.isoformat()


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer takes a string with Tag body or a list of strings, if many=True.
    Deserializer returns a string representation of Tag or a list of them.
    """
    class Meta:
        model = Tag
        fields = ['body', ]

    def to_internal_value(self, data):
        if not isinstance(data, str):
            msg = _('Expected a string, received {}.'.format(type(data)))
            raise ValidationError(msg)
        return {'body': data}

    def to_representation(self, obj):
        return obj.body

    def create(self, validated_data):
        tag = Tag.objects.get_or_create(**validated_data)[0]
        return tag


class PostSerializer(serializers.ModelSerializer):
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    favorited = serializers.SerializerMethodField()
    author = ProfileSerializer(read_only=True)
    tagList = TagSerializer(many=True, required=False, source='tags')

    class Meta:
        model = Post
        fields = [
            'slug', 'title', 'body', 'tagList', 'createdAt', 'updatedAt',
            'favorited', 'likes', 'dislikes', 'author'
        ]
        read_only_fields = ['slug']

    def validate(self, args):
        if args == {}:
            msg = _('No data were provided.')
            raise ValidationError(msg)
        user = self.context.get('user', None)
        if user is None or not user.is_authenticated:
            msg = _('You must pass a valid user in order to perform this operation.')
            raise ValidationError(msg)
        args['author'] = user.profile
        args['slug'] = unique_slugify(
            model=self.Meta.model,
            text=args['title']
        )
        return args

    def create(self, validated_data):
        tag_data_list = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_data in tag_data_list:
            tag = Tag.objects.get_or_create(**tag_data)[0]
            post.tags.add(tag)
        return post

    def update(self, instance, validated_data):
        new_tags = validated_data.pop('tags', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if new_tags:
            old_tags = {tag['body'] for tag in instance.tags.values('body')}
            new_tags = {tag['body'] for tag in new_tags}
            tags_to_add = new_tags.difference(old_tags)
            tags_to_remove = old_tags.difference(new_tags)
            for tag_body in tags_to_add:
                tag = Tag.objects.get_or_create(body=tag_body)[0]
                instance.tags.add(tag)
            for tag_body in tags_to_remove:
                tag = Tag.objects.get(body=tag_body)
                instance.tags.remove(tag)
        return instance

    def get_likes(self, post):
        return post.get_likes()

    def get_dislikes(self, post):
        return post.get_dislikes()

    def get_favorited(self, post):
        user = self.context.get('user', None)
        if user and user.is_authenticated:
            return user.profile.has_in_favorites(post)
        return False

    def get_created_at(self, post):
        return post.created_at.isoformat()

    def get_updated_at(self, post):
        return post.modified_at.isoformat()
