from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password

from users.serializers import UserModelSerializer

class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = UserModelSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            User.objects.create_user(**s.validated_data)
            return Response(
                data={"message": "User successfully registered"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = User.objects.all()
        serializer = UserModelSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserModelSerializer(user)
        return Response(data=serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user.pk != user.pk:
            raise PermissionDenied(detail="you have no power here")
        serializer = UserModelSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data={"message": "user updated"})

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user.pk != user.pk:
            raise PermissionDenied(detail="you have no power here")
        serializer = UserModelSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data={"message": "user partial updated"})

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user.pk != user.pk:
            raise PermissionDenied(detail="you have no power here")
        user.delete()
        return Response(data={"message": "user has been deleted"})
