from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, RegisterResponseSerializer, RegisterSerializer, UserSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

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
        
class UserViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    http_method_names = ['get', 'put', 'patch']
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.objects.filter(email=self.request.user.email)