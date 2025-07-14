from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User


class IsOwnerOrAdmin(BasePermission):
    """
    Пускаем только владельца объекта или администратора.
    ❗ Работает только с ModelViewSet, где obj — это User или модель с полем `user`.

    Аргументы метода has_permission:
        request (rest_framework.request.Request): HTTP-запрос
        view (rest_framework.viewsets.ModelViewSet): вьюха (можно использовать .action)

    Аргументы метода has_object_permission:
        obj (models.Model): объект, к которому проверяется доступ (обычно результат .get_object())

    Возвращает:
        bool: True — доступ разрешён, False — доступ запрещён
    """

    def has_permission(self, request: Request, view: ModelViewSet) -> bool:
        # Разрешаем только авторизованным (в том числе админам)
        return request.user.is_authenticated

    def has_object_permission(
        self, request: Request, view: ModelViewSet, obj: User | None
    ):
        if request.user.is_staff:
            return True # Пускаем админов
        if isinstance(obj, User):
            return obj == request.user    
