from rest_framework.permissions import SAFE_METHODS, BasePermission


class SafeMethodPermission(BasePermission):
    """
    Операции на чтение разрешены всем, остальные операции
    только администратору. Во всех остальных случаях -
    метод не разрешен, ответ от сервера 405.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
