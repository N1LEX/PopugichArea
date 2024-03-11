from djoser import serializers as djoser_serializers

from app.models import User


class UserSerializer(djoser_serializers.UserSerializer):
    class Meta:
        model = User
        fields = ('public_id', 'username', 'full_name', 'role', 'email')
        extra_kwargs = {'password': {'write_only': True}}
