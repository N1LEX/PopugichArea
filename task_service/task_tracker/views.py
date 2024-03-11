from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from task_tracker.models import Task
from task_tracker import permissions
from task_tracker.serializers import TaskSerializer
from task_tracker.tasks import assign_tasks


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, name="Assign Tasks", permission_classes=[permissions.IsAdminOrManager])
    def assign(self, request):
        assign_tasks.delay()
        return Response({'message': 'tasks assign has started'})

    @action(detail=True,  name="Complete Task", permission_classes=[permissions.IsAssigned])
    def complete(self, request, pk=None):
        self.get_object().complete()
        return Response({'message': 'OK'})

    @action(detail=False, name="My Tasks")
    def popug_tasks(self, request):
        self.queryset = self.queryset.filter(user=self.request.user)
        return super().list(request)
