from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions
from rest_framework.request import Request


class IsAuthenticated(permissions.IsAuthenticated):

    def has_permission(self, request: Request, view):
        return not isinstance(request.user, AnonymousUser)
