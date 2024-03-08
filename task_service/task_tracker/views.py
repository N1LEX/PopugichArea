from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from task_tracker.models import Task
from task_tracker.serializers import TaskSerializer
from task_tracker.tasks import shuffle_tasks


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=False, methods=['get'], name="Assign Tasks")
    def assign(self, request):
        """
        shuffle open tasks between users
        """
        shuffle_tasks.delay()
        return Response({'message': 'tasks assign has started'})

    @action(detail=True, methods=['patch'], name="Mark as completed")
    def mark_complete(self, request, pk=None):
        self.get_object().make_completed()
        return Response({'message': 'OK'})
