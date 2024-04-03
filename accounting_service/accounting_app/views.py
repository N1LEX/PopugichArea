import datetime
from datetime import date

from django.db.models.functions import Coalesce, TruncDate

from accounting_app.models import Account, Task, Transaction
from django.db.models import Sum, F, Case, When, IntegerField, Value
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting_app.serializers import SERIALIZERS, SerializerNames
from accounting_app.streaming import EventVersions


class AccountingView(APIView):
    """
    Аккаунтинг: кто сколько денег заработал
    Админам и менеджерам доступна статистика заработанным деньгам по дням
    Остальным доступна только информация о текущем балансе и лог операций
    """

    def get(self, request, *kwargs):
        if self.request.user.is_manager:
            return Response(self._get_management_data())
        return Response(self._get_worker_data())

    def _get_management_data(self):
        stats = Transaction.objects\
            .annotate(date=TruncDate('datetime'))\
            .values('date')\
            .annotate(profit=Coalesce(Sum('credit') - Sum('debit'), Value(0)))\
            .order_by('-date')\
            .values('date', 'profit')

        today = stats[0] if stats else {'date': date.today(), 'profit': 0}

        return {
            'today': today,
            'history': list(stats),
        }

    def _get_worker_data(self):
        transactions = Transaction.objects \
            .select_related('account') \
            .filter(account__user=self.request.user) \
            .annotate(
                amount=Case(
                    When(type=Transaction.TypeChoices.WITHDRAW, then=-F('credit')),
                    default=F('debit'),
                    output_field=IntegerField(),
                ),
            )\
            .values('type', 'amount', 'purpose', 'datetime')

        return {
            'balance': self.request.user.account.balance,
            'transactions': list(transactions),
        }
