from rest_framework import serializers
from .models.store import Store

class StoreSerializer(serializers.ModelSerializer):
    seller_name = serializers.ReadOnlyField(source='seller.display_name')
    
    class Meta:
        model = Store
        fields = [
            'id', 'seller', 'seller_name', 'name', 'slug', 'description', 
            'logo', 'banner', 'is_active', 'is_approved', 'approved_at', 
            'rejection_reason', 'is_suspended', 'suspended_reason', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'slug', 'is_approved', 'approved_at', 'rejection_reason', 
            'is_suspended', 'suspended_reason', 'seller'
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        if not hasattr(user, 'seller_profile'):
            raise serializers.ValidationError("Only users with a seller profile can open a store.")
        
        profile = user.seller_profile
        if not profile.is_verified:
            raise serializers.ValidationError("Your seller profile must be verified before opening a store.")
        
        if not profile.onboarding_completed:
            raise serializers.ValidationError("Please complete your onboarding before opening a store.")
            
        return attrs

class StoreApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['is_approved', 'rejection_reason']

    def validate(self, attrs):
        if not attrs.get('is_approved') and not attrs.get('rejection_reason'):
            raise serializers.ValidationError({"rejection_reason": "Required if rejecting the store."})
        return attrs
