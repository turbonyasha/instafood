from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import UserSerializer, UserCreateSerializer

from .models import FoodgramUser, Subscription
from core.utils import Base64ImageField
from recipes.models import Recipe


class UserIsSubscribedMixin:
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            subscriptions = user.subscriptions.all()  # Получаем все подписки
            return subscriptions.filter(author=obj.author).exists()
        return False


class CustomUserSerializer(UserIsSubscribedMixin, UserSerializer):
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

    # def get_avatar(self, obj):
    #     return obj.get_avatar_url()
    
    # def get_is_subscribed(self, obj):
    #     user = self.context['request'].user
    #     return user.subscriptions.filter(user=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

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
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class RecipesSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = FoodgramUser
        fields = ('avatar',)


class SubscribtionSerializer(UserIsSubscribedMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(source='author.id')  # Получаем ID подписанного пользователя
    email = serializers.EmailField(source='author.email')  # Email подписанного пользователя
    username = serializers.CharField(source='author.username')  # Имя пользователя
    first_name = serializers.CharField(source='author.first_name')  # Имя
    last_name = serializers.CharField(source='author.last_name')  # Фамилия
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='author.avatar')  # Аватар подписанного пользователя

    class Meta:
        model = Subscription  # Используем модель Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def validate(self, data):
        user = self.context['request'].user
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError('Вы не можете подписаться на самого себя.')
        return data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request:
            recipes_limit = request.GET.get('recipes_limit')
            if recipes_limit and recipes_limit.isdigit():
                recipes = Recipe.objects.filter(author=obj.author)[:int(recipes_limit)]
            else:
                recipes = Recipe.objects.filter(author=obj.author)
        return RecipesSubscriptionSerializer(
            recipes,
            many=True).data
