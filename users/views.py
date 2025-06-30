from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import time
from rest_framework.views import APIView
from users.models import UserProfile
from users.serializers import (
    PhoneAuthRequestSerializer, PhoneAuthConfirmSerializer,
    UserProfileSerializer, InviteCodeActivateSerializer
)
from users.serializers import UserModelSerializer, UserSerializer
from users.models import Codes, UserProfile

PHONE_CODE_STORAGE = {}

class PhoneAuthRequestView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = PhoneAuthRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        code = f"{random.randint(1000, 9999)}"
        PHONE_CODE_STORAGE[phone] = code
        time.sleep(random.uniform(1, 2)) 
        return Response({"message": "Код отправлен"})

class PhoneAuthConfirmView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = PhoneAuthConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        if PHONE_CODE_STORAGE.get(phone) != code:
            return Response({"error": "Неверный код"}, status=400)
        user, created = User.objects.get_or_create(username=phone, defaults={"is_active": True})
        profile, _ = UserProfile.objects.get_or_create(user=user, phone=phone)
        return Response({"message": "Авторизация успешна", "invite_code": profile.invite_code})

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

class InviteCodeActivateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = InviteCodeActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['invite_code']
        profile = request.user.profile
        if profile.activated_invite_code:
            return Response({"error": "Инвайт-код уже активирован", "activated_invite_code": profile.activated_invite_code}, status=400)
        try:
            inviter = UserProfile.objects.get(invite_code=code)
        except UserProfile.DoesNotExist:
            return Response({"error": "Инвайт-код не найден"}, status=404)
        profile.activated_invite_code = code
        profile.invited_by = inviter
        profile.save()
        return Response({"message": "Инвайт-код активирован", "activated_invite_code": code})

class RegistrationViewSet(ViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserModelSerializer,
        responses={
            201: "User successfully registered",
            400: "error",
            409: "conflict error"
        }
    )
    def create(self, request: Request) -> Response:
        s = UserModelSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.validated_data["is_active"] = False
        try:
            user = User.objects.create_user(**s.validated_data)
            code = Codes(user=user)
            code.save()
            return Response(
                data={"message": "User successfully registered"},
                status=status.HTTP_201_CREATED # Лучше 201
            )
        except Exception as e:
            return Response(
                data={"error": str(e)},
                status=status.HTTP_409_CONFLICT
            )


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @staticmethod
    def check_user(request: Request, pk: int) -> User:
        user = get_object_or_404(User, pk=pk)
        if request.user.pk != user.pk:
            raise PermissionDenied(detail="you have no power here")
        return user

    @action(
        detail=True, methods=["GET"],
        url_path="activate",
        url_name="activate"
    )
    def activation_page(
        self, request: Request, pk: int
    ) -> Response:
        user = get_object_or_404(User, pk=pk)
        code = request.query_params.get("code")
        obj: Codes = get_object_or_404(Codes, user=user, code=code)
        now = timezone.now()
        diff = now - obj.created_at
        if diff.seconds > 180:
            raise PermissionDenied()
        user.is_active = True
        user.save()
        return Response(data={"message": "activation success!"})

    @swagger_auto_schema(
        responses={200: UserSerializer(many=True)}
    )
    def list(self, request: Request) -> Response:
        queryset = User.objects.all() # Достаем пользователей
        paginator = CustomPageNumberPagination() # объявляем пагинатор
        items = paginator.paginate_queryset(
            queryset=queryset, request=request
        ) # делим юзеров на кучки
        serializer = UserSerializer(
            instance=items, many=True
        ) # в сериализатор передаем кучки пользователей
        return paginator.get_paginated_response(
            data=serializer.data
        ) # вывод с пагинацией

    @swagger_auto_schema(
        responses={
            200: UserSerializer,
            404: "User not found"
        }
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(data=serializer.data)

    @swagger_auto_schema(
        request_body=UserModelSerializer,
        responses={
            200: "user updated",
            400: "serializer not valid",
            403: "forbidden",
            404: "user not found"
        }
    )
    def update(self, request: Request, pk: int) -> Response:
        user = self.check_user(request=request, pk=pk)
        serializer = UserModelSerializer(
            instance=user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={"message": "user updated"})

    @swagger_auto_schema(
        request_body=UserModelSerializer,
        responses={
            200: "user partial updated",
            400: "serializer not valid",
            403: "forbidden",
            404: "user not found"
        }
    )
    def partial_update(self, request: Request, pk: int) -> Response:
        user = self.check_user(request=request, pk=pk)
        serializer = UserModelSerializer(
            instance=user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={"message": "user partial updated"})

    @swagger_auto_schema(
        responses={
            200: "user has been deleted",
            403: "forbidden",
            404: "user not found"
        }
    )
    def destroy(self, request: Request, pk: int) -> Response:
        user = self.check_user(request=request, pk=pk)
        user.delete()
        return Response(
            data={"message": "user has been deleted"}
        )


