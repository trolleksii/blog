from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, ListCreateAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet

from .models import Comment, Post, Tag
from .serializers import CommentSerializer, PostSerializer, TagSerializer


class ListTagsAPIView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def list(self, request):
        queryset = Tag.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'tagList': serializer.data}, status=status.HTTP_200_OK)


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Post.objects.all()
    lookup_field = 'slug'

    def create(self, request, *args, **kwargs):
        data = request.data.get('post', {})
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
        if post.author != request.user.profile:
            return Response({}, status=status.HTTP_403_FORBIDDEN)
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
        qset = self.get_queryset()
        serializer = self.serializer_class(
            qset,
            context={'user': request.user},
            many=True
        )
        return Response({'posts': serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.author != request.user.profile:
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response('', status=status.HTTP_200_OK)

    def retrieve(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        serializer = self.serializer_class(
            post,
            context={'user': request.user}
        )
        return Response({'post': serializer.data}, status=status.HTTP_200_OK)

    @detail_route(methods=['post', 'delete'], permission_classes=[IsAuthenticated], url_name='favorite')
    def favorite(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        if self.request.method == 'POST':
            request.user.profile.favorite(post)
        else:
            request.user.profile.unfavorite(post)
        serializer = self.serializer_class(
            post,
            context={'user': request.user}
        )
        return Response({'post': serializer.data}, status=status.HTTP_200_OK)

    @detail_route(methods=['post', 'delete'], permission_classes=[IsAuthenticated], url_name='like')
    def like(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        if post.author.user != request.user:
            # user can't like/dislike his own posts
            if not request.user.profile.has_voted_for(post):
                # user votes only once, and can't change his vote
                if self.request.method == 'POST':
                    request.user.profile.like(post)
                else:
                    request.user.profile.dislike(post)
        serializer = self.serializer_class(
            post,
            context={'user': request.user}
        )
        return Response({'post': serializer.data}, status=status.HTTP_200_OK)


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
        data = request.data.get('comment', {})
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
        if comment.author != request.user.profile:
            return Response(status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_200_OK)
