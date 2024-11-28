from django.db.models import Count, Exists, OuterRef
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

import core.constants as const
from core.filters import UserFilterSet
from core.paginations import LimitPageNumberPagination
from core.permissions import IsAuthorOrAdmin

from .models import FoodgramUser, Subscription
from .serializers import (CustomTokenCreateSerializer, CustomUserSerializer,
                          SubscribtionSerializer)


class CustomUserViewSet(UserViewSet):
    """Представление для пользователя."""
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

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_anonymous:
            return queryset
        subscribe = self.request.user.subscriptions.filter(
            author=OuterRef('pk')
        )
        queryset = queryset.annotate(
            is_subscribed_annotated=Exists(subscribe),
            recipes_count=Count('recipe')
        )
        return queryset

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        """Реализация обновления и удаления аватарки."""
        user = self.request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            return Response(request.data, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        """Реализация добавления и удаления подписки на автора."""
        self.permission_classes = [IsAuthenticated]
        user = self.request.user
        try:
            author = FoodgramUser.objects.get(id=id)
        except FoodgramUser.DoesNotExist:
            return Response(
                {'detail': const.USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'detail': const.SUBSCRIBTION_MYSELF},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription, created = Subscription.objects.get_or_create(
                user=user, author=author
            )
            if not created:
                return Response(
                    {'detail': const.SUBSCRIBTION_ALREADY},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribtionSerializer(
                subscription, context={'request': request, 'user': user}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                subscription = Subscription.objects.get(
                    user=user, author=author
                )
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscription.DoesNotExist:
                return Response(
                    {'detail': const.SUBSCRIPTION_NOTFOUND},
                    status=status.HTTP_404_NOT_FOUND
                )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Представление для списка подписок"""
    serializer_class = SubscribtionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        author = serializer.validated_data['author']
        if user == author:
            raise serializers.ValidationError(const.SUBSCRIBTION_MYSELF)
        subscription, created = Subscription.objects.get_or_create(
            user=user, author=author
        )
        if not created:
            raise serializers.ValidationError(const.SUBSCRIBTION_ALREADY)
        return subscription

    def perform_destroy(self, instance):
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_user_token(request):
    """Получение токена пользователя по email и паролю."""
    serializer = CustomTokenCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = FoodgramUser.objects.get(
            email=serializer.validated_data['email']
        )
    except FoodgramUser.DoesNotExist:
        raise ValidationError(const.AUTH_FAIL_TEXT)
    if not user.check_password(serializer.validated_data['password']):
        raise ValidationError(const.AUTH_FAIL_TEXT)
    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {'auth_token': token.key},
        status=status.HTTP_200_OK
    )
