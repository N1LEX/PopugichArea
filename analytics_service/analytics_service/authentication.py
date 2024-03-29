import requests
from django.conf import settings
from rest_framework.request import Request
from rest_framework_simplejwt import authentication

from analytics_app.models import User


class Authentication(authentication.JWTStatelessUserAuthentication):

    def authenticate(self, request: Request):
        auth_response = requests.post(settings.AUTH_URL, json={'refresh': request.COOKIES.get('refresh')})
        if auth_response.status_code != 200:
            return None
        auth_data = auth_response.json()
        user = User.objects.get(public_id=auth_data['public_id'])
        return user, auth_data['access']
