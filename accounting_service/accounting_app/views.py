from datetime import date

from accounting_app.models import Account, Task, Transaction
from accounting_app.serializers import get_serializer, SerializerNames
from accounting_app.streaming import EventVersions
from django.db.models import Sum, F
from rest_framework.response import Response
from rest_framework.views import APIView


class AccountingView(APIView):
    """
    Аккаунтинг: кто сколько денег заработал
    Админам и менеджерам доступна статистика заработанным деньгам по дням
    Остальным доступна только информация о текущем балансе и лог операций
    """
    def get(self, request, *kwargs):
        serializer = self.get_serializer_class()
        queryset = self.get_queryset()
        return Response(data=serializer(**queryset))

    def get_serializer_class(self):
        version = self.request.query_params.get('version', EventVersions.v1)
        if self.request.user.is_manager:
            return get_serializer(SerializerNames.MANAGEMENT_EARNING_STATS, version)
        return get_serializer(SerializerNames.ACCOUNT_STATE, version)

    def get_queryset(self):
        if self.request.user.is_manager:
            sum_annotation = Sum('assigned_price', default=0) + Sum('completed_price', default=0)

            current_date_stats = Task.objects\
                .filter(date=date.today)\
                .annotate(sum=sum_annotation)\
                .values('sum', 'date')

            # Group by date
            history_earnings_stats = Task.objects \
                .values('date') \
                .annotate(sum=sum_annotation) \
                .order_by('-date') \
                .values('sum', 'date')

            return {
                'current_date': current_date_stats,
                'history': history_earnings_stats,
            }

        transactions = Transaction.objects \
            .select_related('account') \
            .filter(account__user=self.request.user) \
            .annotate(display_amount=F('display_amount')) \
            .values()

        account_state = Account.objects \
            .filter(user=self.request.user) \
            .prefetch_related('transactions') \
            .annotate(transactions=transactions) \
            .values('balance', 'transactions')[:1]

        return account_state
