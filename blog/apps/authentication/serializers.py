from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, serializers
from .models import User


class LoginSerializer(serializers.Serializer):
    """
    Handles user login. Takes username and password and checks if this
    user exists and active.
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )
    about = serializers.CharField(read_only=True)
    pic = serializers.URLField(read_only=True)
    email = serializers.EmailField(read_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        user = authenticate(username=username, password=password)
        if user is None:
            msg = _('Incorrect credentials')
            raise exceptions.AuthenticationFailed(msg)
        return {
            'username': user.username,
            'email': user.email,
            'about': user.profile.about,
            'pic': user.profile.pic,
            'token': user.token,
        }


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Handles user registration process. In addition creates a profile
    for each added user.
    """
    about = serializers.CharField(source='profile.about', read_only=True)
    pic = serializers.URLField(source='profile.pic', read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'about', 'pic', 'token']
        extra_kwargs = {
            'token': {'read_only': True},
            'password': {
                'max_length': 128,
                'min_length': 8,
                'write_only': True,
            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Handles serialization of user information, including profile information.
    """
    about = serializers.CharField(source='profile.about', required=False)
    pic = serializers.URLField(source='profile.pic', required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'about', 'pic', 'token']
        extra_kwargs = {
            'token': {'read_only': True},
            'username': {'read_only': True},
            'password': {
                'max_length': 128,
                'min_length': 8,
                'write_only': True,
            }
        }

    def update(self, instance, validated_data):
        if validated_data:
            password = validated_data.pop('password', None)
            # extract profile-related data
            profile = validated_data.pop('profile', None)
            for key, value in validated_data.items():
                setattr(instance, key, value)
            if password:
                instance.set_password(password)
            # reflect changes in user profile
            if profile:
                for key, value in profile.items():
                    setattr(instance.profile, key, value)
                instance.profile.save()
            instance.save()
        return instance
