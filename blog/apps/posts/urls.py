from django.urls import re_path

from rest_framework.routers import DefaultRouter

from .views import ListTagsAPIView, PostViewSet

app_name = 'posts'

router = DefaultRouter(trailing_slash=False)

router.register(r'posts', PostViewSet, base_name='posts')

urlpatterns = [
    re_path(r'^tags$', ListTagsAPIView.as_view(), name='listtags_view'),
] + router.urls
