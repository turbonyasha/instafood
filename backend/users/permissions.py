from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_safe_method(request):
    """Проверка на безопасность метода."""
    return request.method in SAFE_METHODS


class AdminOnlyPermission(BasePermission):
    """Доступ только администратору."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class AdminOrSafeMethodPermission(AdminOnlyPermission):
    """
    Разрешает доступ всем пользователям для безопасных методов запроса,
    в остальных случаях — только администраторам.
    """
    def has_permission(self, request, view):
        return (
            is_safe_method(request)
            or super().has_permission(request, view)
        )


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
    """
    Операции на чтение разрешены всем, остальные - автору текста,
    администратору или модератору.
    """

    admin = AdminOnlyPermission()

    def has_permission(self, request, view):
        if is_safe_method(request):
            return True
        return (
            request.user.is_authenticated
            or self.admin.has_permission(request, view)
        )

    def has_object_permission(self, request, view, obj):
        if is_safe_method(request):
            return True
        return (
            obj.author == request.user
            or self.admin.has_permission(request, view)
        )
