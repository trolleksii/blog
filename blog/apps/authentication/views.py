from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView

from .serializers import LoginSerializer, RegistrationSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserSerializer(user).data
        return Response({"user": user_data}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        credentials = request.data.get('user', {})
        serializer = self.serializer_class(data=credentials)
        serializer.is_valid(raise_exception=True)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)


class UserView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

    def update(self, request):
        user = request.user
        data = request.data.get('user', {})
        serializer = self.serializer_class(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)
