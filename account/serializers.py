from rest_framework import serializers
from core.models import User



class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "is_active",
            "is_phone_verified",
            "date_joined"
        ]