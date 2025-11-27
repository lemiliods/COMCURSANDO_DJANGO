from rest_framework import serializers
from .models import AdminUser


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo AdminUser.
    """
    
    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class LoginSerializer(serializers.Serializer):
    """
    Serializer para autenticação de login.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
