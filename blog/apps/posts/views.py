from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, ListCreateAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet

from apps.core.shortcuts import get_object_or_404

from .models import Comment, Post, Tag
from .serializers import CommentSerializer, PostSerializer, TagSerializer
from .pagination import PostsPaginaton


class ListTagsAPIView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def list(self, request):
        response = super(ListTagsAPIView, self).list(self, request)
        response.data = {'tagList': response.data}
        return response


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Post.objects.all()
    pagination_class = PostsPaginaton
    lookup_field = 'slug'

    def get_queryset(self):
        qset = super(PostViewSet, self).get_queryset()
        tag = self.request.GET.get('tag', None)
        author = self.request.GET.get('author', None)
        favorited = self.request.GET.get('favorited', None)
        if author:
            qset = qset.filter(author__user__username=author)
        if tag:
            qset = qset.filter(tags__body=tag)
        if favorited:
            qset = qset.filter(favorited_by__user__username=favorited)
        return qset

    def create(self, request, *args, **kwargs):
        data = request.data.get('post', None)
        serializer = self.serializer_class(
            data=data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'post': serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, slug, *args, **kwargs):
        data = request.data.get('post', {})
        post = get_object_or_404(Post, slug=slug)
        request_maker = request.user.profile
        if not request_maker.is_author_of(post):
            raise PermissionDenied
        serializer = self.serializer_class(
            post,
            data=data,
            context={'user': request.user},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'post': serializer.data}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        qset = self.get_queryset().order_by('-created_at', '-modified_at')
        page = self.paginate_queryset(qset)
        serializer = self.serializer_class(
            page,
            context={'user': request.user},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    def destroy(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        request_maker = request.user.profile
        if not request_maker.is_author_of(post):
            raise PermissionDenied
        post.delete()
        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        serializer = self.serializer_class(
            post,
            context={'user': request.user}
        )
        return Response({'post': serializer.data}, status=status.HTTP_200_OK)

    @detail_route(methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated], url_name='favorite')
    def favorite(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        request_maker = request.user.profile
        if request.method == 'POST':
            request_maker.favorite(post)
        else:
            request_maker.unfavorite(post)
        serializer = self.serializer_class(
            post,
            context={'user': request.user}
        )
        return Response({'post': serializer.data}, status=status.HTTP_200_OK)

    @detail_route(methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated], url_name='like')
    def like(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        request_maker = request.user.profile
        if request.method == 'POST':
            request_maker.like(post)
        else:
            request_maker.dislike(post)
        serializer = self.serializer_class(
            post,
            context={'user': request.user}
        )
        return Response({'post': serializer.data}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'], permission_classes=[IsAuthenticated], url_name='feed')
    def feed(self, request):
        user = request.user
        qset = Post.objects.filter(author__in=user.profile.followees.all())
        qset = qset.order_by('-created_at', '-modified_at')
        page = self.paginate_queryset(qset)
        serializer = self.serializer_class(
            page,
            context={'user': request.user},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class CommentListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = CommentSerializer

    def list(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        qset = Comment.objects.filter(post=post)
        serializer = self.serializer_class(
            qset,
            context={'user': request.user},
            many=True)
        return Response({'comments': serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        data = request.data.get('comment', None)
        serializer = self.serializer_class(
            data=data,
            context={'user': request.user, 'post': post}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'comment': serializer.data}, status=status.HTTP_201_CREATED)


class CommentDestroyAPIView(DestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = CommentSerializer

    def destroy(self, request, slug, pk, *args, **kwargs):
        comment = get_object_or_404(Comment, post__slug=slug, pk=pk)
        request_maker = request.user.profile
        if not request_maker.is_author_of(comment):
            raise PermissionDenied
        comment.delete()
        return Response(status=status.HTTP_200_OK)
