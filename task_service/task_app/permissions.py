from rest_framework import permissions

from task_app.models import User


class IsAdminOrManager(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role in (User.RoleChoices.ADMIN, User.RoleChoices.MANAGER)
