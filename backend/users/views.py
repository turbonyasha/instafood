from rest_framework.decorators import action
from rest_framework import status, permissions, mixins, viewsets
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)

from djoser.views import UserViewSet, TokenCreateView

from .models import FoodgramUser, Subscription
from .serializers import CustomUserSerializer, CustomTokenCreateSerializer, SubscribtionSerializer
from recipes.models import Recipe


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

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request, pk=None):
        user = self.request.user
        serializer = SubscribtionSerializer(user.subscriptions.all(), many=True, context={'request': request, 'user': user})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        user = self.request.user
        try:
            author = FoodgramUser.objects.get(id=id)
        except FoodgramUser.DoesNotExist:
            return Response({'detail': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            if user == author:
                return Response({'detail': 'Вы не можете подписаться на самого себя.'}, status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response({'detail': 'Вы уже подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)
            subscription = Subscription(user=user, author=author)
            subscription.save()
            serializer = SubscribtionSerializer(subscription, context={'request': request, 'user': user})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                subscription = Subscription.objects.get(user=user, author=author)
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscription.DoesNotExist:
                return Response({'detail': 'Подписка не найдена.'}, status=status.HTTP_404_NOT_FOUND)


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


class SubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Возвращает список подписок пользователя."""
    serializer_class = SubscribtionSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.subscriptions.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        