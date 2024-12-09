from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrSafeMethodPermission(BasePermission):
    """
    Операции на чтение разрешены всем, остальные операции
    только администратору. Во всех остальных случаях -
    метод не разрешен, ответ от сервера 405.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
