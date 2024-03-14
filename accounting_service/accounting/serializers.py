from rest_framework import serializers

from accounting.models import Account, Log


class AdminAccountingSerializer(serializers.Serializer):
    earning_amount = serializers.IntegerField()


class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = ('amount', 'purpose')


class UserAccountingSerializer(serializers.ModelSerializer):
    logs = LogSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ('balance', 'logs')
