from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrSafeMethodPermission(BasePermission):
    """
    Операции на чтение разрешены всем, остальные операции
    только автору.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
