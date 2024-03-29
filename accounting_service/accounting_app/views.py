from datetime import date

from accounting_app.models import Account, Task, Transaction
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
        if self.request.user.is_manager:
            return Response(self._management_queryset())
        return Response(self._worker_queryset())

    def get_queryset(self):
        if self.request.user.is_manager:
            return self._management_queryset()
        return self._worker_queryset()

    def _management_queryset(self):
        sum_annotation = Sum('assigned_price', default=0) + Sum('completed_price', default=0)

        current_date_stats = Task.objects \
            .filter(date=date.today()) \
            .annotate(sum=sum_annotation) \
            .values('sum', 'date')

        # Group by date
        history_stats = Task.objects \
            .values('date') \
            .annotate(sum=sum_annotation) \
            .order_by('-date') \
            .values('sum', 'date')

        return {
            'today': list(current_date_stats),
            'history': list(history_stats),
        }

    def _worker_queryset(self):
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
