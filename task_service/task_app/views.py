import attrs
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from task_app import permissions
from task_app.models import Task
from task_app.serializers import get_serializer, SerializerNames
from task_app.streaming import EventVersions, EventStreaming
from task_app.tasks import assign_tasks, task_completed


class TaskTrackerView(ViewSet):
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
    queryset = Task.objects.select_related('user')

    def create(self, request, *args, **kwargs):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = get_serializer(SerializerNames.TASK, version)
        task_model = serializer(description=request.data.get('description'))
        task = Task.create(task_model)
        created_model = serializer.from_object(task)
        event_streaming = EventStreaming(version)
        event_streaming.task_created(created_model)
        return Response(attrs.asdict(created_model), status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = get_serializer(SerializerNames.TASK, version)
        tasks = [attrs.asdict(serializer.from_object(task)) for task in self.queryset]
        return Response(tasks)

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
        version = request.query_params.get('version', EventVersions.v1)
        task_completed.delay(version)
        return Response({'message': 'OK'})

    @action(detail=False, name="My Tasks")
    def my(self, request: Request):
        self.queryset = self.queryset.filter(user=self.request.user, status=Task.StatusChoices.ASSIGNED)
        return self.list(request)
