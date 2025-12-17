from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from core.models import User
from account.models import SellerProfile, CustomerProfile
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token["email"] = user.email
        token["role"] = user.role
        token["is_phone_verified"] = user.is_phone_verified
        
        return token

class RegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})
    
    class Meta:
        model = User
        fields = ["email", "password", "password2", "phone", "role"]
    
    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise  serializers.ValidationError({"password": "Passwords do not match"})
        else:
            return attrs
    
    def validate_role(self, value):
        if value == User.Role.STAFF:
            raise serializers.ValidationError(
                "Staff accounts can only be created by admin."
            )
        return value
    
    def create(self, validated_data):
        role = validated_data.pop("role", User.Role.CUSTOMER)
        password = validated_data.pop("password")
        validated_data.pop("password2", None)
        
        with transaction.atomic():
            user = User.objects.create_user(
                password=password,
                role=role,
                **validated_data,
            )

            PROFILE_CREATORS = {
                User.Role.CUSTOMER: lambda u: CustomerProfile.objects.create(user=u),
                User.Role.SELLER: lambda u: SellerProfile.objects.create(user=u, is_verified=False),
            }

        return user

class RegisterResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role"]

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)
    is_phone_verified = serializers.BooleanField(read_only=True)
    class Meta:
        model = User
        fields = ["email", "phone", "is_2fa_enabled", "is_phone_verified", "role"]
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    new_password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    new_password2 = serializers.CharField(write_only=True, style={"input_type": "password"})
    
    def validate(self, attrs):
        if  not self.context["request"].user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Passwords do not match"})
        return attrs
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance
    
    class Meta:
        model = User
        fields = ["old_password", "new_password", "new_password2"]
        

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate(self, attrs):
        try:
            self.user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist"})
        return attrs


class EmailConfirmedSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    
    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid uid"})
        
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError({"token": "Invalid token"})
        return attrs
    
    def save(self, **kwargs):
        self.user.is_email_verified = True
        self.user.save()
        return self.user

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate(self, attrs):
        try:
            self.user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise NotFound("User with this email does not exist")
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})
    
    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid uid"})
    
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError({"token": "Invalid token"})
        
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs
    
    def save(self, **kwargs):
        self.user.set_password(self.validated_data["password"])
        self.user.save()
        return self.user