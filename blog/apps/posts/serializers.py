from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from apps.posts.models import Comment, Post, Tag
from apps.profiles.serializers import ProfileSerializer


class CommentSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at')
    modifiedAt = serializers.DateTimeField(source='modified_at')

    class Meta:
        model = Comment
        fields = ['title', 'body', 'createdAt', 'modifiedAt', 'author']
        read_only_fields = ['createdAt', 'modifiedAt', 'author']

    def validate(self, args):
        user = self.context.get('user', None)
        if user is None or not user.is_authenticated:
            message = 'user not authenticated'
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')
        post = self.context.get('post', None)
        if post is None:
            message = 'post not specified'
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')
        args['author'] = user.profile
        args['post'] = post
        return args


class TagSerializer(serializers.ModelSerializer):
    """
    Serialixer takes a string with Tag body or a list of strings, if many=True.
    Deserializer returns a string representation of Tag or a list of them.
    """
    class Meta:
        model = Tag
        fields = ['body', ]

    def to_internal_value(self, data):
        if not isinstance(data, str):
            message = 'expected list of strings, got list of {}'.format(type(data))
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')
        return {
            'body': data,
            'slug': slugify(data)
        }

    @property
    def data(self):
        return super(serializers.Serializer, self).data

    def to_representation(self, obj):
        return obj.body

    def create(self, validated_data):
        return self.Meta.model.objects.get_or_create(**validated_data)[0]


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
        user = self.context.get('user', None)
        if user is None or not user.is_authenticated:
            message = 'user not authenticated'
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')
        args['author'] = user.profile
        # TODO generate unique slugs
        args['slug'] = slugify(args['title'])
        return args

    def create(self, validated_data):
        tag_data_list = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_data in tag_data_list:
            tag = Tag.objects.get_or_create(**tag_data)[0]
            post.tags.add(tag)
        return post

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
        return str(post.created_at)

    def get_updated_at(self, post):
        return str(post.modified_at)
