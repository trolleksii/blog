from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Read-only serializer that returns information about the profile, and checks
    if request maker follows this profile.
    """
    username = serializers.CharField(source='user.username')
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username', 'about', 'pic', 'following']
        read_only_fields = ['username', 'about', 'pic', 'following']

    def get_following(self, obj):
        """
        Check if request maker follows profile viewed.
        """
        user = self.context.get('user', None)
        if user and user.is_authenticated:
            return user.profile.has_in_followees(obj)
        return False


class ProfileRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        return value.user.username


class ProfileFolloweesSerializer(serializers.ModelSerializer):
    """
    Read-only serializer that returns list of usernames followed by request
    maker.
    """
    followees = ProfileRelatedField(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['followees', ]
