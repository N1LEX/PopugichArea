import attrs
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from task_app import permissions
from task_app.models import Task
from task_app.serializers import get_serializer, SerializerNames
from task_app.streaming import EventVersions
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
    queryset = Task.objects.all()
    # permission_classes = [IsManager]

    def list(self, request, *args, **kwargs):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = get_serializer(SerializerNames.TASK, version)
        tasks = [attrs.asdict(serializer(**task)) for task in self.queryset.values()]
        return Response(data=tasks)

    def get_serializer_class(self):
        version = self.request.query_params.get('version', EventVersions.v1)
        print(self.queryset)
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
