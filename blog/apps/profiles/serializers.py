from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Read-only serializer that returns information about the profile, and checks
    if request maker follows it.
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
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return request.user.profile.has_in_followees(obj)
        return False


class ProfileRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        return value.user.username


class ProfileFolloweesSerializer(serializers.ModelSerializer):
    """
    Read-only serializer that returns list of profile followees usernames.
    """
    followees = ProfileRelatedField(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['followees', ]
