from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

import core.constants as const
from core.models import Base64ImageField
from recipes.models import Recipe

from .models import FoodgramUser, Subscription


class UserIsSubscribedMixin:
    """Миксин для проверки подписки."""
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if isinstance(obj, FoodgramUser):
                return Subscription.objects.filter(
                    user=user, author=obj
                ).exists()
            elif isinstance(obj, Subscription):
                return Subscription.objects.filter(
                    user=user, author=obj.author
                ).exists()
        return False


class CustomUserSerializer(UserIsSubscribedMixin, UserSerializer):
    """Сериализатор для чтения пользователя."""
    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = FoodgramUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomTokenCreateSerializer(serializers.Serializer):
    """Сериализатор для выдачи токенов."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class RecipesSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецепта в подписках."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватарки."""
    avatar = Base64ImageField()

    class Meta:
        model = FoodgramUser
        fields = ('avatar',)


class SubscribtionSerializer(
    UserIsSubscribedMixin,
    serializers.ModelSerializer
):
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='author.avatar')

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count', 'avatar'
        )

    def validate(self, data):
        user = self.context['request'].user
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                const.VALID_SUBSCRIBE
            )
        return data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request:
            recipes_limit = request.GET.get('recipes_limit')
            if recipes_limit and recipes_limit.isdigit():
                recipes = Recipe.objects.filter(
                    author=obj.author
                )[:int(recipes_limit)]
            else:
                recipes = Recipe.objects.filter(author=obj.author)
        return RecipesSubscriptionSerializer(
            recipes,
            many=True).data
