from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TagSerializer


class ListTagsAPIView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = TagSerializer

    def get(self, request):
        queryset = self.serializer_class.Meta.model.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'tagList': serializer.data}, status=status.HTTP_200_OK)
