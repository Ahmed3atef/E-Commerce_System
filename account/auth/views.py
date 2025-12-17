from drf_spectacular.utils import OpenApiResponse
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import (CustomTokenObtainPairSerializer, 
                          RegisterResponseSerializer, 
                          RegisterSerializer, 
                          UserSerializer,
                          ChangePasswordSerializer,
                          ForgotPasswordSerializer,
                          ResetPasswordSerializer,
                          EmailVerificationSerializer,
                          EmailConfirmedSerializer,
                          )



User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        request={
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "password": {"type": "string", "format": "password"}
            },
            "required": ["email", "password"]
        },
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "access": {"type": "string"},
                        "refresh": {"type": "string"}
                    }
                },
                description="Login successful",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                        },
                    )
                ]
            ),
            401: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"}
                    }
                },
                description="Invalid credentials",
                examples=[
                    OpenApiExample(
                        "Invalid Credentials",
                        value={"detail": "No active account found with the given credentials"},
                    )
                ]
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "email": {"type": "array", "items": {"type": "string"}},
                        "password": {"type": "array", "items": {"type": "string"}}
                    }
                },
                description="Validation errors",
                examples=[
                    OpenApiExample(
                        "Missing Fields",
                        value={
                            "email": ["This field is required."],
                            "password": ["This field is required."]
                        },
                    )
                ]
            ),
        },
        description="Obtain JWT token pair (access and refresh tokens). The access token contains custom claims: email, role, and is_phone_verified.",
        summary="Login - Obtain Token Pair"
    )
    def get_serializer_class(self):
        return CustomTokenObtainPairSerializer

class RegisterView(APIView):
    http_method_names = ['post']
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=RegisterResponseSerializer,
                description="User registered successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "id": 1,
                            "email": "user@example.com",
                            "role": "customer"
                        },
                    )
                ]
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "email": {"type": "array", "items": {"type": "string"}},
                        "password": {"type": "array", "items": {"type": "string"}},
                    }
                },
                description="Validation errors",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={
                            "email": ["Enter a valid email address."],
                            "password": ["Passwords do not match"]
                        }
                    )
                ]
            ),
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_serializer = RegisterResponseSerializer(user)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
 
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="Password changed successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "id": 1,
                            "email": "user@example.com",
                            "username": "john_doe",
                            # Add other UserSerializer fields here
                        },
                    )
                ]
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "old_password": {"type": "array", "items": {"type": "string"}},
                        "new_password": {"type": "array", "items": {"type": "string"}},
                    }
                },
                description="Validation errors",
                examples=[
                    OpenApiExample(
                        "Incorrect Old Password",
                        value={"old_password": ["Old password is incorrect"]},
                    ),
                    OpenApiExample(
                        "Passwords Don't Match",
                        value={"new_password": ["Passwords do not match"]},
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided"
            ),
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(request.user, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = UserSerializer(request.user)
        return Response(response_serializer.data,
                        status=status.HTTP_200_OK)
       

class EmailVerificationView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=EmailVerificationSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    }
                },
                description="Verification email sent",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"message": "Verification email sent successfully"}
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Validation errors",
                examples=[
                    OpenApiExample(
                        "User Not Found",
                        value={"email": ["User with this email does not exist"]}
                    )
                ]
            )
        }
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.user = getattr(serializer, "user", None)
        if self.user:
            token = default_token_generator.make_token(self.user)
            uid = urlsafe_base64_encode(force_bytes(self.user.pk))
            
            reset_path = reverse("auth:auth-confirm-email", kwargs={"uid": uid, "token": token})
            reset_link = f"{request.build_absolute_uri(reset_path)}"
            send_mail(
                'Email Verification',
                f'Click the link to verify your email: {reset_link}',
                'noreply@ecommerce.com',
                [self.user.email],
                fail_silently=False,
            )
            
        return Response({"message": "Verification email sent successfully"})

class EmailConfirmedView(APIView):
    http_method_names = ['get']
    permission_classes = [AllowAny]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='uid',
                type=str,
                location=OpenApiParameter.PATH,
                description='Base64 encoded user ID'
            ),
            OpenApiParameter(
                name='token',
                type=str,
                location=OpenApiParameter.PATH,
                description='Email verification token'
            ),
        ],
        request=None,  # GET requests don't have a request body
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    }
                },
                description="Email verified successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"message": "Email verified successfully"},
                    )
                ]
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "token": {"type": "string"}
                    }
                },
                description="Invalid or expired token",
                examples=[
                    OpenApiExample(
                        "Invalid Token",
                        value={"token": "Invalid or expired token"},
                    )
                ]
            ),
            404: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"}
                    }
                },
                description="Invalid confirmation link",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"detail": "Invalid or expired confirmation link"},
                    )
                ]
            ),
        }
    )
    def get(self, request, uid, token):
        data = {"uid": uid, "token": token}
        serializer = EmailConfirmedSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # This calls the update method in your serializer
        return Response({"message": "Email verified successfully"})

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    }
                },
                description="Password reset email sent successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"message": "Password reset email has been sent"},
                    )
                ]
            ),
            404: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"}
                    }
                },
                description="User not found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"detail": "User with this email does not exist"},
                    )
                ]
            ),
        }
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.user = getattr(serializer, "user", None)
        if self.user:
            token = default_token_generator.make_token(self.user)
            uid = urlsafe_base64_encode(force_bytes(self.user.pk))
            
            reset_path = reverse("auth:auth-reset-password", kwargs={"uid": uid, "token": token})
            reset_link = f"{request.build_absolute_uri(reset_path)}"
            
            send_mail(
                'Password Reset',
                f'Click the link to reset your password: {reset_link}',
                'noreply@ecommerce.com',
                [self.user.email],
                fail_silently=False,
            )
        return Response({"message": "If email exists, reset link was sent"})
        
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='uid',
                type=str,
                location=OpenApiParameter.PATH,
                description='Base64 encoded user ID'
            ),
            OpenApiParameter(
                name='token',
                type=str,
                location=OpenApiParameter.PATH,
                description='Password reset token'
            ),
        ],
        request=None,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string"},
                        "token": {"type": "string"}
                    }
                },
                description="Token validated",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"uid": "Mg", "token": "abc-123456"}
                    )
                ]
            )
        }
    )
    def get(self, request, uid, token):
        return Response({'uid': uid, 'token': token})
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='uid',
                type=str,
                location=OpenApiParameter.PATH,
                description='Base64 encoded user ID'
            ),
            OpenApiParameter(
                name='token',
                type=str,
                location=OpenApiParameter.PATH,
                description='Password reset token'
            ),
        ],
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    }
                },
                description="Password reset successful",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"message": "Password reset successful"}
                    )
                ]
            ),
            400: OpenApiResponse(description="Validation errors")
        }
    )
    def post(self, request, uid, token):
        data = request.data.copy()
        data['uid'] = uid
        data['token'] = token
        
        serializer = ResetPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save() 
        return Response({"message": "Password reset successful"})

