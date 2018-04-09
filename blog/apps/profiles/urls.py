from django.urls import re_path

from .views import ProfileAPIView, ProfileFollowAPIView, ProfileFolloweesAPIView

app_name = 'profiles'

urlpatterns = [
    re_path(r'^profile/followees$', ProfileFolloweesAPIView.as_view(), name='followees_view'),
    re_path(r'^profiles/(?P<username>\w+)$', ProfileAPIView.as_view(), name='profile_view'),
    re_path(r'^profiles/(?P<username>\w+)/follow$', ProfileFollowAPIView.as_view(), name='follow_view'),
]
