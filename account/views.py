from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import User
from .serializers import AdminUserUpdateSerializer, UserListSerializer, UserDetailSerializer, MeSerializer
from rest_framework.permissions import IsAuthenticated
from account.auth.permissions import IsStaffUser

    
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = MeSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UserViewSet(ModelViewSet):
    http_method_names = ["get", "patch", "put"]
    queryset = User.objects.all()
    permission_classes = [IsStaffUser]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["role", "is_active"]
    ordering_fields = ["date_joined", "email"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action in ["update", "partial_update"]:
            return AdminUserUpdateSerializer
        return UserListSerializer
