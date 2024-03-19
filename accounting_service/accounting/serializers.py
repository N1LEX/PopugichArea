from rest_framework import serializers

from accounting.models import Account, Transaction


class EarningStatsSerializer(serializers.Serializer):
    sum = serializers.IntegerField()
    date = serializers.DateField()


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('type', 'display_amount', 'purpose', 'datetime')


class UserAccountingSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ('balance', 'transactions')
