import attrs
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from task_app import permissions
from task_app.models import Task
from task_app.serializers import SerializerNames, SERIALIZERS
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
    def get_queryset(self):
        return Task.objects.all()

    def create(self, request, *args, **kwargs):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = SERIALIZERS[version][SerializerNames.TASK]
        task_model = serializer(description=request.data.get('description'))
        task = Task.create(task_model)
        created_model = serializer.from_object(task)
        event_streaming = EventStreaming(version)
        event_streaming.task_created(created_model)
        return Response(attrs.asdict(created_model), status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = SERIALIZERS[version][SerializerNames.TASK_DASHBOARD]
        tasks = [attrs.asdict(serializer.from_object(task)) for task in self.get_queryset()]
        return Response(tasks)

    def retrieve(self, request, pk):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = SERIALIZERS[version][SerializerNames.TASK_DASHBOARD]
        task = Task.objects.get(pk=pk)
        return Response(attrs.asdict(serializer.from_object(task)))

    def get_serializer_class(self):
        version = self.request.query_params.get('version', EventVersions.v1)
        return SERIALIZERS[version][SerializerNames.TASK]

    @action(detail=False, name="Assign Tasks", permission_classes=[permissions.IsAdminOrManager])
    def assign(self, request: Request):
        version = request.query_params.get('version', EventVersions.v1)
        assign_tasks.delay(version)
        return Response({'message': 'tasks assign has started'})

    @action(detail=True,  name="Complete Task")
    def complete(self, request: Request, pk):
        task = Task.objects.get(pk=pk)
        if task.user == request.user:
            task.complete()
            version = request.query_params.get('version', EventVersions.v1)
            task_completed.delay(task.pk, version)
            return Response({'message': 'OK'})
        return Response({'message': 'You can complete only your task'})

    @action(detail=False, name="My Tasks")
    def my(self, request: Request):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = SERIALIZERS[version][SerializerNames.TASK_DASHBOARD]
        queryset = self.get_queryset().filter(user=self.request.user, status=Task.StatusChoices.ASSIGNED)
        tasks = [attrs.asdict(serializer.from_object(task)) for task in queryset]
        return Response(tasks)
