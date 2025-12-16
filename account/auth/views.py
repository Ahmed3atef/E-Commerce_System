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
from drf_spectacular.utils import extend_schema
from .permissions import IsStaffUser
from .serializers import (CustomTokenObtainPairSerializer, 
                          RegisterResponseSerializer, 
                          RegisterSerializer, 
                          UserSerializer,
                          ChangePasswordSerializer,
                          ForgotPasswordSerializer,
                          ResetPasswordSerializer,
                          EmailVerificationSerializer,
                          EmailConfirmedSerializer
                          )



User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        responses={200: CustomTokenObtainPairSerializer}
    )
    def get_serializer_class(self):
        return CustomTokenObtainPairSerializer

class RegisterView(APIView):
    http_method_names = ['post']
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=RegisterSerializer,
        responses={201: RegisterResponseSerializer}
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
 
@extend_schema(
    responses={200: UserSerializer(many=True)}
)
class UsersStuffListView(APIView):
     permission_classes = [IsAuthenticated, IsStaffUser]
     
     
     def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
        
class MeView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={200: UserSerializer}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: UserSerializer}
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
        responses={200: UserSerializer}
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.user = getattr(serializer, "user", None)
        if self.user:
            token = default_token_generator.make_token(self.user)
            uid = urlsafe_base64_encode(force_bytes(self.user.pk))
            
            reset_path = reverse("account:auth-confirm-email")
            reset_link = f"{request.build_absolute_uri(reset_path)}{uid}/{token}/"
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
        request=EmailConfirmedSerializer,
        responses={200: EmailConfirmedSerializer}
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
        responses={200: UserSerializer}
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.user = getattr(serializer, "user", None)
        if self.user:
            token = default_token_generator.make_token(self.user)
            uid = urlsafe_base64_encode(force_bytes(self.user.pk))
            
            reset_path = reverse("account:auth-reset-password")
            reset_link = f"{request.build_absolute_uri(reset_path)}{uid}/{token}/"
            
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
        request=ResetPasswordSerializer,
        responses={200: UserSerializer}
    )
    def post(self, request, uidb64, token):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.user = getattr(serializer, "user", None)
        if self.user:
            self.user.set_password(serializer.validated_data["password"])
            self.user.save()
        return Response({"message": "Password reset successful"})

