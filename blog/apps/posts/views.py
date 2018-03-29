from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Post
from .serializers import PostSerializer, TagSerializer


class ListTagsAPIView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = TagSerializer

    def get(self, request):
        queryset = self.serializer_class.Meta.model.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'tagList': serializer.data}, status=status.HTTP_200_OK)


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()
    lookup_field = 'slug'
