from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (CustomTokenObtainPairSerializer, 
                          RegisterResponseSerializer, 
                          RegisterSerializer, 
                          UserSerializer,
                          ChangePasswordSerializer)
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

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