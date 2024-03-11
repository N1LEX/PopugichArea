from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions
from rest_framework.request import Request

from task_tracker.models import User


class IsAuthenticated(permissions.IsAuthenticated):

    def has_permission(self, request: Request, view):
        return not isinstance(request.user, AnonymousUser)


class IsAdminOrManager(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role in (User.RoleChoices.ADMIN, User.RoleChoices.MANAGER)


class IsAssigned(permissions.BasePermission):

    def has_permission(self, request, view):
        task = view.get_object()
        return task.user == request.user
