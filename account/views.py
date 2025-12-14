from django_filters import filterset
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models import User
from .serializers import UserListSerializer
from account.auth.permissions import IsStaffUser


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsStaffUser]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["role", "is_active"]
    ordering_fields = ["date_joined", "email"]