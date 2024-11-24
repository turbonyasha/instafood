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
    # """
    # Разрешает доступ всем пользователям для безопасных методов запроса,
    # в остальных случаях — только администраторам.
    # """
    # def has_permission(self, request, view):
    #     return (
    #         is_safe_method(request)
    #         or super().has_permission(request, view)
    #     )
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True  # Разрешить доступ всем для GET
        elif request.user and request.user.is_authenticated:
            # Для других методов проверка прав пользователя
            if request.user.is_staff:  # Здесь проверка на админа
                return True
            else:
                # Для остальных методов не разрешаем доступ
                raise MethodNotAllowed("Method Not Allowed")
        else:
            # Если пользователь не аутентифицирован, доступ не разрешен
            return False


class IsAuthorOrAdmin(BasePermission):
    """
    Операции на чтение разрешены всем, остальные - автору текста,
    администратору или модератору.
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
