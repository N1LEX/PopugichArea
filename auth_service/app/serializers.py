from djoser.serializers import UserSerializer

from app.models import User


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('public_id', 'username', 'full_name', 'role', 'email')
        extra_kwargs = {'password': {'write_only': True}}
