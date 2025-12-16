from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from account.auth.permissions import IsStaffUser
from account.auth.serializers import (UserSerializer,)


User = get_user_model()

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
