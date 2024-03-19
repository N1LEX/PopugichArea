from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import views
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import User
from app.serializers import UserSerializer


class SigninView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return render(request, 'signin.html')


class UserCreateView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer


class AuthenticateAppView(GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        try:
            refresh = RefreshToken(request.data['refresh'], verify=True)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'public_id': refresh.payload['public_id'],
            })
        except TokenError:
            return Response(status=401)


class TokenCreateView(views.TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        response = HttpResponseRedirect(redirect_to='http://localhost:8002/task/')
        response.set_cookie(
            'access',
            serializer.validated_data['access'],
            max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        )
        response.set_cookie(
            'refresh',
            serializer.validated_data['refresh'],
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        )
        return response
