from rest_framework.decorators import action
from rest_framework import status, permissions, mixins, viewsets
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny, IsAdminUser
)

from djoser.views import UserViewSet, TokenCreateView

from .models import FoodgramUser, Subscription
from .serializers import CustomUserSerializer, CustomTokenCreateSerializer, SubscribtionSerializer, AvatarSerializer
from recipes.models import Recipe, FavoriteRecipes, RecipeIngredient
from core.permissions import AdminOnlyPermission, IsAuthorOrAdmin
from core.utils import LimitPageNumberPagination


class CustomUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'avatar' or self.action == 'subscribe' or self.action == 'subscriptions':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthorOrAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        self.permission_classes = [IsAuthenticated]
        user = self.request.user

        if request.method == 'PUT':
            if not request.data:
                return Response({'detail': 'Запрос не содержит данных.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = AvatarSerializer(user, data=request.data, partial=True)
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
        self.permission_classes = [IsAuthenticated]
        user = self.request.user
        subscriptions = user.subscriptions.all()
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscribtionSerializer(page, many=True, context={'request': request, 'user': user})
            return self.get_paginated_response(serializer.data)
        serializer = SubscribtionSerializer(subscriptions, many=True, context={'request': request, 'user': user})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        self.permission_classes = [IsAuthenticated]
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