from django.db import models
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting.models import Account, User, Task
from accounting.serializers import AdminAccountingSerializer, UserAccountingSerializer


class AccountingView(APIView):

    def get(self, request, *kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()
        return Response(serializer(queryset).data)

    def get_serializer_class(self):
        if self.request.user.role in (User.RoleChoices.ADMIN, User.RoleChoices.ACCOUNTANT):
            return AdminAccountingSerializer
        return UserAccountingSerializer

    def get_queryset(self):
        if self.request.user.role in (User.RoleChoices.ADMIN, User.RoleChoices.ACCOUNTANT):
            return Task.objects.aggregate(
                earning_amount=Sum('assigned_price', default=0) + Sum('completed_price', default=0),
            )
        return Account.objects.filter(user=self.request.user).prefetch_related('logs').get()
