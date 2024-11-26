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
from django.db.models import Exists, OuterRef, Count

from djoser.views import UserViewSet, TokenCreateView

from .models import FoodgramUser, Subscription
from .serializers import CustomUserSerializer, CustomTokenCreateSerializer, SubscribtionSerializer, AvatarSerializer
from recipes.models import Recipe, FavoriteRecipes, RecipeIngredient
from core.permissions import AdminOnlyPermission, IsAuthorOrAdmin
from core.utils import LimitPageNumberPagination
from core.filters import UserFilterSet


from django.db.models import Exists, OuterRef, Count
from rest_framework.permissions import AllowAny, IsAuthenticated


class CustomUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all().order_by('id')
    serializer_class = CustomUserSerializer
    pagination_class = LimitPageNumberPagination
    filterset_class = UserFilterSet

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [AllowAny()]
        if self.action in ['avatar', 'subscribe', 'subscriptions']:
            return [IsAuthenticated()]
        return [IsAuthorOrAdmin()]

    # def get_queryset(self):
    #     # Получаем базовый queryset
    #     queryset = self.queryset

    #     # Если пользователь анонимный, просто возвращаем весь список
    #     if self.request.user.is_anonymous:
    #         return queryset

    #     # Создаем подзапрос, который проверяет, подписан ли текущий пользователь на других пользователей
    #     subscribe = self.request.user.subscriptions.filter(author=OuterRef('pk'))

    #     # Добавляем аннотацию is_subscribed через подзапрос
    #     queryset = queryset.annotate(
    #         is_subscribed_annotated=Exists(subscribe),  # Используем Exists для подзапроса
    #         recipes_count=Count('recipe')   # Подсчет количества рецептов
    #     )

    #     return queryset

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        user = self.request.user
        # Получаем queryset с подписками
        queryset = self.get_queryset().filter(is_subscribed=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribtionSerializer(page, many=True, context={'request': request, 'user': user})
            return self.get_paginated_response(serializer.data)
        
        # Если пагинация не нужна, возвращаем все подписки
        serializer = SubscribtionSerializer(queryset, many=True, context={'request': request, 'user': user})
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
            
            # Создание или получение подписки
            subscription, created = Subscription.objects.get_or_create(user=user, author=author)
            
            if not created:
                return Response({'detail': 'Вы уже подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)

            # Сериализация подписки
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