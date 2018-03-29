from django.urls import re_path

from .views import ListTagsAPIView

app_name = 'posts'

urlpatterns = [
    re_path(r'^tags$', ListTagsAPIView.as_view(), name='listtags_view'),
]
