import attrs
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from analytics_app.models import Stats
from analytics_app.permissions import IsManager
from analytics_app.serializers import MostExpensiveTaskRequest, get_serializer, SerializerNames
from analytics_app.streaming import EventVersions


class StatsView(ViewSet):
    """
    Общая статистика по всем дням.
    Запросить самую дорогую:
        Example: /must_expensive_task?start_date=2023-03-01&end_date=2023-03-20
    """
    queryset = Stats.objects.select_related('most_expensive_task')
    permission_classes = [IsManager]

    def list(self, request, *args, **kwargs):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = get_serializer(SerializerNames.Stats, version)
        return Response({
            'today': attrs.asdict(serializer.from_object(self.queryset.latest('date'))),
            'history': attrs.asdict(serializer.from_queryset(self.queryset)),
        })

    @action(detail=False)
    def most_expensive_task(self, request: Request):
        request_serializer = MostExpensiveTaskRequest(**request.data)
        most_expensive_task = Stats.get_most_expensive_task(request_serializer.start_date, request_serializer.end_date)
        if most_expensive_task:
            task_serializer = get_serializer(SerializerNames.TASK, request_serializer.version)
            task_model = task_serializer.from_object(most_expensive_task)
            return Response(attrs.asdict(task_model))
        return Response({})
