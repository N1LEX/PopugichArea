from django.db.models import Max
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from analytics_service.app.models import DayStats
from analytics_service.app.permissions import IsManager
from analytics_service.app.serializers import MostExpensiveTaskRequest, get_serializer, SerializerNames
from analytics_service.app.streaming import EventVersions


class CurrentDayStatsView(RetrieveModelMixin, GenericViewSet):
    queryset = DayStats.objects.latest('date')
    permission_classes = [IsManager]

    def get_serializer_class(self):
        version = self.request.query_params.get('version', EventVersions.v1)
        return get_serializer(SerializerNames.DayStats, version)


class AllDaysStatsView(ListModelMixin, GenericViewSet):
    """
    Общая статистика по всем дням.
    Запросить самую дорогую:
        Example: /must_expensive_task?start_date=2023-03-01&end_date=2023-03-20
    """
    queryset = DayStats.objects.select_related('task').all()
    permission_classes = [IsManager]

    def get_serializer_class(self):
        version = self.request.query_params.get('version', EventVersions.v1)
        return get_serializer(SerializerNames.DayStats, version)

    @action(detail=False)
    def must_expensive_task(self, request: Request):
        serializer = MostExpensiveTaskRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.queryset().filter(
            date__range=(
                serializer.validated_data['start_date'],
                serializer.validated_data['end_date']
            ),
            most_expensive_task__completed_price=Max('most_expensive_task__completed_price')
        ).aggregate(must_expensive_task=Max('must_expensive_task'))
