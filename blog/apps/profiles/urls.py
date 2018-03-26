from django.urls import re_path

from .views import ProfileView, ProfileFollowView, ProfileFolloweesView

app_name = 'profiles'

urlpatterns = [
    re_path(r'^profile/followees$', ProfileFolloweesView.as_view(), name='followees_view'),
    re_path(r'^profiles/(?P<username>\w+)$', ProfileView.as_view(), name='profile_view'),
    re_path(r'^profiles/(?P<username>\w+)/follow$', ProfileFollowView.as_view(), name='follow_view'),
]
