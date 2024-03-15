from rest_framework import serializers

from accounting.models import Account, Log


class EarningStatsSerializer(serializers.Serializer):
    sum = serializers.IntegerField()
    date = serializers.DateField()


class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = ('amount', 'purpose')


class UserAccountingSerializer(serializers.ModelSerializer):
    logs = LogSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ('balance', 'logs')
