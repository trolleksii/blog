from rest_framework import permissions, status, views
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import Profile
from .serializers import ProfileFolloweesSerializer, ProfileSerializer


class ProfileAPIView(views.APIView):
    """
    Returns profile information by username parameter.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProfileSerializer

    def get(self, request, username, *args, **kwargs):
        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound
        serializer = self.serializer_class(profile, context={'user': request.user})
        return Response({'profile': serializer.data}, status=status.HTTP_200_OK)


class ProfileFollowAPIView(views.APIView):
    """
    Handles profile fllows/unfollows. Request maker is the follower, followee
    is identified by username parameter.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProfileSerializer

    def post(self, request, username, *args, **kwargs):
        follower = request.user.profile
        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound
        follower.follow(followee)
        serializer = self.serializer_class(followee, context={'user': request.user})
        return Response({'profile': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, username, *args, **kwargs):
        follower = request.user.profile
        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound
        follower.unfollow(followee)
        serializer = self.serializer_class(followee, context={'user': request.user})
        return Response({'profile': serializer.data}, status=status.HTTP_200_OK)


class ProfileFolloweesAPIView(views.APIView):
    """
    Shows list of all followees of currently authenticated user.
    """
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ProfileFolloweesSerializer

    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        serializer = self.serializer_class(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
