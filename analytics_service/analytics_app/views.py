import attrs
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from analytics_app.models import Stats, Account
from analytics_app.permissions import IsManager
from analytics_app.serializers import MostExpensiveTaskRequest, SerializerNames, SERIALIZERS
from analytics_app.streaming import EventVersions


class StatsView(ViewSet):
    """
    Общая статистика по всем дням.
    Запросить самую дорогую:
        Example: /must_expensive_task?start_date=2023-03-01&end_date=2023-03-20
    """
    permission_classes = [IsManager]

    def list(self, request, *args, **kwargs):
        queryset = Stats.objects.select_related('most_expensive_task')
        version = self.request.query_params.get('version', EventVersions.v1)
        serializer = SERIALIZERS[version][SerializerNames.STATS]
        return Response({
            'today': attrs.asdict(serializer.from_object(queryset.latest('date'))),
            'history': [attrs.asdict(stats) for stats in serializer.from_queryset(queryset)],
        })

    @action(detail=False)
    def most_expensive_task(self, request: Request):
        request_serializer = MostExpensiveTaskRequest(**request.data)
        most_expensive_task = Stats.get_most_expensive_task(request_serializer.start_date, request_serializer.end_date)
        if most_expensive_task:
            task_serializer = SERIALIZERS[request_serializer.version][SerializerNames.TASK]
            task_model = task_serializer.from_object(most_expensive_task)
            return Response(attrs.asdict(task_model))
        return Response({})
