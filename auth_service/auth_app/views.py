import attrs
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import views
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.models import User
from auth_app.serializers import SerializerNames, SERIALIZERS
from auth_app.streaming import EventVersions, EventStreaming


class SigninView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return render(request, 'signin.html')


class UserCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        event_version = request.query_params.get('version', EventVersions.v1)
        user_signup_serializer = SERIALIZERS[event_version][SerializerNames.USER_SIGNUP]
        user_signup_model = user_signup_serializer(**request.data)
        user = User.create(attrs.asdict(user_signup_model))

        user_serializer = SERIALIZERS[event_version][SerializerNames.USER]
        user_model = user_serializer.from_object(user)
        event_streaming = EventStreaming(event_version)
        event_streaming.user_created(user_model)
        return Response(attrs.asdict(user_model))


class AuthenticateAppView(GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        refresh_token = request.data['refresh']
        if refresh_token is None:
            return Response(status=401)
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

        response = HttpResponseRedirect(redirect_to='http://192.168.0.103:8002/')
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
