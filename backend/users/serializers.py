from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from djoser.serializers import UserSerializer, UserCreateSerializer


from .models import FoodgramUser, Subscription
from recipes.serializers import Base64ImageField


class CustomUserSerializer(UserSerializer):
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

    def get_avatar(self, obj):
        return obj.get_avatar_url()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, author=obj).exists()
        return False


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
