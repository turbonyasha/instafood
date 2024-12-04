from rest_framework.exceptions import MethodNotAllowed, NotAuthenticated
from rest_framework.permissions import SAFE_METHODS, BasePermission


# def is_safe_method(request):
#     """Проверка на безопасность метода."""
#     return request.method in SAFE_METHODS


class SafeMethodPermission(BasePermission):
    """
    Операции на чтение разрешены всем, остальные операции
    только администратору. Во всех остальных случаях -
    метод не разрешен, ответ от сервера 405.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            # return NotAuthenticated('User is not authenticated')
        # elif request.user and request.user.is_authenticated:
        #     if request.user.is_staff:
        #         return True
        #     else:
        #         raise MethodNotAllowed('Method Not Allowed')
        # else:
            return False
