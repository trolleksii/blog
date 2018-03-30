from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import Post
from .serializers import PostSerializer, TagSerializer


class ListTagsAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def get(self, request):
        queryset = self.serializer_class.Meta.model.objects.all()
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
        return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, slug, *args, **kwargs):
        data = request.data.get('post', {})
        try:
            instance = self.serializer_class.Meta.model.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise Http404
        if instance.author != request.user.profile:
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(
            instance,
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
        try:
            post = self.serializer_class.Meta.model.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise Http404
        if post.author != request.user.profile:
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response('', status=status.HTTP_200_OK)

    def retrieve(self, request, slug, *args, **kwargs):
        try:
            instance = self.serializer_class.Meta.model.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise Http404
        serializer = self.serializer_class(
            instance,
            context={'user': request.user}
        )
        return Response({'post': serializer.data}, status=status.HTTP_200_OK)

    @detail_route(methods=['post', 'delete'], permission_classes=[IsAuthenticated], url_name='favorite')
    def favorite(self, request, slug):
        try:
            post = self.serializer_class.Meta.model.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise Http404
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
        try:
            post = self.serializer_class.Meta.model.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise Http404
        operation_status = status.HTTP_403_FORBIDDEN
        if post.author.user != request.user:
            # user can't like/dislike his own posts
            if not request.user.profile.has_voted_for(post):
                # user votes only once, and can't change his vote
                if self.request.method == 'POST':
                    request.user.profile.like(post)
                else:
                    request.user.profile.dislike(post)
                operation_status = status.HTTP_200_OK
        serializer = self.serializer_class(
            post,
            context={'user': request.user}
        )
        return Response({'post': serializer.data}, status=operation_status)
