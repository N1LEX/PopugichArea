from rest_framework.permissions import BasePermission

from task_app.models import User


class IsAdminOrManager(BasePermission):

    def has_permission(self, request, view):
        return isinstance(request.user, User) and request.user.is_manager
