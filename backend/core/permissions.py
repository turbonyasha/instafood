from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import MethodNotAllowed


def is_safe_method(request):
    """Проверка на безопасность метода."""
    return request.method in SAFE_METHODS


class AdminOnlyPermission(BasePermission):
    """Доступ только администратору."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_staff
        )


class AdminOrSafeMethodPermission(AdminOnlyPermission):
    """
    Операции на чтение разрешены всем, остальные операции
    только администратору. Во всех остальных случаях -
    метод не разрешен, ответ от сервера 405.
    """

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        elif request.user and request.user.is_authenticated:
            if request.user.is_staff:
                return True
            else:
                raise MethodNotAllowed("Method Not Allowed")
        else:
            return False


class IsAuthorOrAdmin(BasePermission):
    """
    Операции на чтение разрешены всем, остальные -
    автору рецепта, администратору.
    """
    admin = AdminOnlyPermission()

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or self.admin.has_permission(request, view)
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or self.admin.has_permission(request, view)
        )
