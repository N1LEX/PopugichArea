from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsAuthenticated(BasePermission):

    def has_permission(self, request: Request, view):
        return not isinstance(request.user, AnonymousUser)
