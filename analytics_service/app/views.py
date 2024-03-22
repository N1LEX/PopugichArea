import attrs
from django.db.models import Max
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.models import Stats
from app.permissions import IsManager
from app.serializers import MostExpensiveTaskRequest, get_serializer, SerializerNames
from app.streaming import EventVersions


class CurrentDayStatsView(ViewSet):
    permission_classes = [IsManager]

    def get(self, request, *kwargs):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = get_serializer(SerializerNames.DayStats, version)
        day_stats = Stats.objects.latest('date')
        return Response(data=attrs.asdict(serializer(day_stats)))


class AllStatsView(ViewSet):
    """
    Общая статистика по всем дням.
    Запросить самую дорогую:
        Example: /must_expensive_task?start_date=2023-03-01&end_date=2023-03-20
    """
    queryset = Stats.objects.select_related('most_expensive_task')
    permission_classes = [IsManager]

    def list(self, request, *args, **kwargs):
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = get_serializer(SerializerNames.AllStats, version)
        return Response(serializer(self.queryset))

    @action(detail=False)
    def most_expensive_task(self, request: Request):
        request_serializer = MostExpensiveTaskRequest(**request.data)
        most_expensive_task = self.queryset().get(
            date__range=(
                request_serializer.start_date,
                request_serializer.end_date,
            ),
            most_expensive_task__completed_price=Max('most_expensive_task__completed_price'),
        )
        task_serializer = get_serializer(SerializerNames.TASK, request_serializer.version)
        return Response(data=task_serializer(most_expensive_task))
