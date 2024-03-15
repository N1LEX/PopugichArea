from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting.models import Account, User, Task
from accounting.serializers import UserAccountingSerializer, EarningStatsSerializer


class AccountingView(APIView):
    """
    Аккаунтинг: кто сколько денег заработал
    Админам и менеджерам доступна статистика заработанным деньгам по дням
    Остальным доступна только информация о текущем балансе и лог операций
    """

    def get(self, request, *kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()
        if serializer == EarningStatsSerializer:
            return Response(serializer(queryset, many=True).data)
        return Response(serializer(queryset).data)

    def get_serializer_class(self):
        if self.request.user.role in (User.RoleChoices.ADMIN, User.RoleChoices.ACCOUNTANT):
            return EarningStatsSerializer
        return UserAccountingSerializer

    def get_queryset(self):
        if self.request.user.role in (User.RoleChoices.ADMIN, User.RoleChoices.ACCOUNTANT):
            return Task.objects.values('date').annotate(
                sum=Sum('assigned_price', default=0) + Sum('completed_price', default=0),
            ).order_by('-date')
        return Account.objects.filter(user=self.request.user).prefetch_related('logs').get()
