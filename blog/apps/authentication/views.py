from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistrationSerializer, UserSerializer


class LoginAPIView(APIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data.get('user', None)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data.get('user', None)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)


class UserAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request):
        serializer = self.serializer_class(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

    def update(self, request):
        data = request.data.get('user', {})
        serializer = self.serializer_class(request.user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)
