from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from task_tracker.models import Task
from task_tracker import permissions
from task_tracker.serializers import TaskSerializer
from task_tracker.tasks import assign_tasks


class TaskViewSet(viewsets.ModelViewSet):
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
    def my(self, request):
        self.queryset = self.queryset.filter(user=self.request.user, status=Task.StatusChoices.ASSIGNED)
        return super().list(request)
