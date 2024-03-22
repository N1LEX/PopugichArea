from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from task_tracker import permissions
from task_tracker.models import Task
from task_tracker.serializers import get_serializer, SerializerNames, TaskV1
from task_tracker.streaming import EventVersions
from task_tracker.tasks import assign_tasks, task_completed


class TaskTrackerView(viewsets.ModelViewSet):
    """
    Таск-трекер: содержит список задач
    Создавать задачи может кто угодно
    Попуг, который будет делать задачу выбирается рандомно (за исключением админов и менеджеров)

    Extra actions:
        Assign tasks: действие доступно админам и менеджерам.
        Взять все открытые задачи и рандомно заассайнить каждую на любого из сотрудников

        My tasks: посмотреть мой список задач

        /task/{id}/complete: отметить задачу завершенной
    """
    queryset = Task.objects.all()
    serializer_class = TaskV1

    def get_serializer_class(self):
        version = self.request.query_params.get('version', EventVersions.v1)
        return get_serializer(SerializerNames.TASK, version)

    @action(detail=False, name="Assign Tasks", permission_classes=[permissions.IsAdminOrManager])
    def assign(self, request: Request):
        version = request.query_params.get('version', EventVersions.v1)
        assign_tasks.delay(version)
        return Response({'message': 'tasks assign has started'})

    @action(detail=True,  name="Complete Task", permission_classes=[permissions.IsAssigned])
    def complete(self, request: Request, pk=None):
        self.get_object().complete()
        event_version = request.query_params.get('event_version', EventVersions.v1)
        task_completed.delay(event_version)
        return Response({'message': 'OK'})

    @action(detail=False, name="My Tasks")
    def my(self, request: Request):
        self.queryset = self.queryset.filter(user=self.request.user, status=Task.StatusChoices.ASSIGNED)
        return super().list(request)
