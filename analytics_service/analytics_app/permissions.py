from rest_framework.permissions import BasePermission

from analytics_app.models import User


class IsManager(BasePermission):

    def has_permission(self, request, view):
        return isinstance(request.user, User) and request.user.is_manager
