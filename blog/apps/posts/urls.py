from django.urls import re_path

from rest_framework.routers import SimpleRouter

from .views import (
    CommentListCreateAPIView, CommentDestroyAPIView, ListTagsAPIView, PostViewSet
)

app_name = 'posts'

router = SimpleRouter(trailing_slash=False)

router.register(r'posts', PostViewSet, base_name='post')

urlpatterns = [
    re_path(r'^tags$', ListTagsAPIView.as_view(), name='listtags_view'),
    re_path(r'^posts/(?P<slug>[^/.]+)/comments$', CommentListCreateAPIView.as_view(), name='comments_view'),
    re_path(r'^posts/(?P<slug>[^/.]+)/comments/(?P<id>\d+)$', CommentDestroyAPIView.as_view(), name='comments_del_view'),
] + router.urls
