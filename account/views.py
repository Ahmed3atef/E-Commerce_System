from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone  # Added import

from account.models.seller import SellerProfile
from core.models import User
from .serializers import (
    AdminUserUpdateSerializer,
    SellerListSerializer,
    UserListSerializer,
    UserDetailSerializer,
    MeSerializer
)
# from account.auth.permissions import IsStaffUser


# class MeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         serializer = MeSerializer(request.user)
#         return Response(serializer.data)

#     def patch(self, request):
#         serializer = MeSerializer(
#             request.user,
#             data=request.data,
#             partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# class UserViewSet(ModelViewSet):
#     http_method_names = ["get", "patch", "head", "options"]  # Added head, options; removed put
#     queryset = User.objects.all()
#     permission_classes = [IsStaffUser]
    
#     filter_backends = [DjangoFilterBackend, OrderingFilter]
#     filterset_fields = ["role", "is_active"]
#     ordering_fields = ["date_joined", "email"]

#     def get_serializer_class(self):
#         if self.action == "retrieve":
#             return UserDetailSerializer
#         elif self.action in ["update", "partial_update"]:
#             return AdminUserUpdateSerializer
#         return UserListSerializer
    
#     def get_queryset(self):
#         # Consider adding filtering for staff users
#         queryset = super().get_queryset()
#         # You might want to exclude superusers or add additional filtering
#         return queryset


# class SellerAdminViewSet(viewsets.ReadOnlyModelViewSet):
    # queryset = SellerProfile.objects.select_related("user").all()
    # serializer_class = SellerListSerializer
    # permission_classes = [IsStaffUser]
    
    # filter_backends = [DjangoFilterBackend, OrderingFilter]
    # filterset_fields = ["is_verified"]
    # ordering_fields = ["approved_at", "user__email"]
    
    # @action(detail=True, methods=["post"], permission_classes=[IsStaffUser])
    # def approve(self, request, pk=None):
    #     seller = self.get_object()

    #     if seller.is_verified:
    #         return Response(
    #             {"detail": "Seller already approved."},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     seller.is_verified = True
    #     seller.approved_at = timezone.now()
    #     seller.save()
        
    #     # Optional: Refresh from database to get updated data
    #     seller.refresh_from_db()

    #     return Response(
    #         {
    #             "detail": "Seller approved successfully.",
    #             "seller": SellerListSerializer(seller).data
    #         },
    #         status=status.HTTP_200_OK,
    #     )