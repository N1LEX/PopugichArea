from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.response import Response

from task_tracker.models import Task
from task_tracker.serializers import TaskSerializer
from task_tracker.tasks import shuffle_tasks


class TasksView(GenericAPIView, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=False, methods=['get'])
    def assign_tasks(self, request):
        """
        shuffle open tasks between users
        """
        shuffle_tasks.delay()
        return Response({'message': 'tasks assign has started'})
