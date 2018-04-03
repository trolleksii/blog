from django.utils.text import slugify

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

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

    def get_created_at(self, comment):
        return str(comment.created_at)

    def get_updated_at(self, comment):
        return str(comment.modified_at)


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
            message = 'expected a string, but got a {}'.format(type(data))
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
            msg = 'User is not authenticated.'
            raise ValidationError({
                'detail': msg})
        if args == {}:
            msg = 'No data were provided.'
            raise ValidationError({
                'detail': msg})
        args['author'] = user.profile
        slug_check = False
        while not slug_check:
            slug = unique_slugify(args['title'])
            if not Post.objects.filter(slug=slug).exists():
                slug_check = True
        args['slug'] = slug
        return args

    def create(self, validated_data):
        tag_data_list = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_data in tag_data_list:
            tag = Tag.objects.get_or_create(**tag_data)[0]
            post.tags.add(tag)
        return post

    def update(self, instance, validated_data):
        tag_data_list = validated_data.pop('tags', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.tags.all().delete()
        for tag_data in tag_data_list:
            tag = Tag.objects.get_or_create(**tag_data)[0]
            instance.tags.add(tag)
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
        return str(post.created_at)

    def get_updated_at(self, post):
        return str(post.modified_at)
