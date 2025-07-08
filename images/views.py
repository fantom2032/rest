from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

from images.models import Gallery, Images, Avatar, Image
from users.models import User
from images.serializers import (
    GallerySerializer, ImagesSerializer, AvatarSerializer, ImageSerializer
)
from publics.models import Public




class GalleryView(ModelViewSet):
    queryset = Gallery.objects.all()
    permission_classes = [AllowAny]
    serializer_class = GallerySerializer


class ImagesView(ModelViewSet):
    queryset = Images.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ImagesSerializer


class AvatarViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request):
        """Загрузка и установка новой аватарки (заменяет старую)"""
        user = request.user
        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.avatar_id:
            Image.objects.filter(pk=user.avatar_id).delete()
        image = serializer.save(owner=user)
        user.avatar = image
        user.save(update_fields=["avatar"])
        return Response(ImageSerializer(image).data, status=status.HTTP_201_CREATED)

class GalleryViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def add_image(self, request):
        """Добавить изображение в галерею пользователя"""
        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.save(owner=request.user)
        return Response(ImageSerializer(image).data, status=status.HTTP_201_CREATED)

class PublicAvatarViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, pk=None):
        """Загрузка и установка новой аватарки для группы"""
        public = get_object_or_404(
            Public.objects.select_related("avatar", "owner").only("id", "avatar", "owner"),
            pk=pk, owner=request.user
        )
        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if public.avatar_id:
            Image.objects.filter(pk=public.avatar_id).delete()
        image = serializer.save(owner=request.user)
        public.avatar = image
        public.save(update_fields=["avatar"])
        return Response(ImageSerializer(image).data, status=status.HTTP_201_CREATED)