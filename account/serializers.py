from rest_framework import serializers
from core.models import User
from account.models import CustomerProfile, StaffProfile, SellerProfile


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
        
class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "phone",
            "is_phone_verified",
        ]
        read_only_fields = ["email", "is_phone_verified"]

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "role",
            "is_active",
        ]
        
class UserDetailSerializer(serializers.ModelSerializer):
    customer_profile = serializers.SerializerMethodField()
    staff_profile = serializers.SerializerMethodField()
    seller_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "is_active",
            "is_phone_verified",
            "date_joined",
            "customer_profile",
            "staff_profile",
            "seller_profile",
        ]

    def get_customer_profile(self, obj):
        if hasattr(obj, "customer_profile"):
            return {
                "first_name": obj.customer_profile.first_name,
                "last_name": obj.customer_profile.last_name,
            }
        return None

    def get_staff_profile(self, obj):
        if hasattr(obj, "staff_profile"):
            return {
                "department": obj.staff_profile.department,
                "employee_id": obj.staff_profile.employee_id,
            }
        return None

    def get_seller_profile(self, obj):
        if hasattr(obj, "seller_profile"):
            return {
                "store_name": obj.seller_profile.store_name,
                "is_verified": obj.seller_profile.is_verified,
            }
        return None
    
class SellerListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source = "user.email", read_only=True)
    
    class Meta:
        model = SellerProfile
        fields = [
            "id",
            "email",
            "display_name",
            "is_verified",
            "approved_at",
        ]