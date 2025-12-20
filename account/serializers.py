from rest_framework import serializers
from account.models import CustomerProfile, SellerProfile, StaffProfile
from address.serializers import AddressSerializer
class CustomerProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)
    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'avatar', 'is_blocked', 'blocked_reason', 'preferred_language', 'marketing_opt_in', 'address', 'created_at']


class SellerProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)
    class Meta:
        model = SellerProfile
        fields = [
            'id', 'user', 'avatar', 'seller_type', 'is_verified', 'onboarding_completed', 
            'verified_at', 'rejected_reason', 'display_name', 'support_email', 
            'support_phone', 'is_blocked', 'blocked_reason', 'preferred_language',
            'address', 'created_at', 'updated_at'
        ]
        
        

class StaffProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)
    class Meta:
        model = StaffProfile
        fields = ['id', 'user', 'avatar', 'department', 'job_title', 'employee_id', 'is_active_staff', 'address', 'created_at']