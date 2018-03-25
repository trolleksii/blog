from django.contrib.auth import authenticate

from rest_framework import serializers

from apps.profiles.models import Profile

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
        username = attrs.get('username', None)
        password = attrs.get('password', None)
        if username is None:
            msg = 'Username is required to log in'
            raise serializers.ValidationError(msg)
        if password is None:
            msg = 'Password is required to log in'
            raise serializers.ValidationError(msg)
        user = authenticate(username=username, password=password)
        if user is None:
            msg = 'Incorrect credentials'
            raise serializers.ValidationError(msg)
        if not user.is_active:
            msg = 'This user has been deactivated'
            raise serializers.ValidationError(msg)
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
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'token']
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
        Profile.objects.create(user=user)
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
        password = validated_data.pop('password', None)
        # extract profile-related data
        profile = validated_data.pop('profile', {})
        for key in validated_data:
            setattr(instance, key, validated_data[key])
        if password:
            instance.set_password(password)
        # reflect changes in user profile
        for key, value in profile.items():
            setattr(instance.profile, key, value)
        instance.profile.save()
        instance.save()
        return instance
