from rest_framework.decorators import action
from rest_framework import status, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet, TokenCreateView

from .models import FoodgramUser
from .serializers import CustomUserSerializer, CustomTokenCreateSerializer


class CustomUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        user = self.request.user

        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            return Response(request.data, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_user_token(request):
    """Получение токена пользователя по email и паролю."""
    serializer = CustomTokenCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = FoodgramUser.objects.get(email=serializer.validated_data['email'])
    except FoodgramUser.DoesNotExist:
        raise ValidationError("Неверный email или пароль.")
    # Проверяем пароль
    if not user.check_password(serializer.validated_data['password']):
        raise ValidationError("Неверный email или пароль.")
    # Получение или создание токена для пользователя
    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {'auth_token': token.key},
        status=status.HTTP_200_OK
    )