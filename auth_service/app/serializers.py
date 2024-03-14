from rest_framework import serializers

from app.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('public_id', 'password', 'username', 'full_name', 'role', 'email')
        extra_kwargs = {'password': {'write_only': True}}
