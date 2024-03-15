from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting.models import Account, User, Task
from accounting.serializers import UserAccountingSerializer, EarningStatsSerializer


class AccountingView(APIView):

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
            )
        return Account.objects.filter(user=self.request.user).prefetch_related('logs').get()
