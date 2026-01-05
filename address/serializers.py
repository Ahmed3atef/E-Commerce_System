from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'type', 'country', 'city', 'street', 'postal_code', 'is_default']
