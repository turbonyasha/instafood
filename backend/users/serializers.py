from rest_framework import serializers, exceptions
from djoser.serializers import UserSerializer, UserCreateSerializer

from .models import FoodgramUser, Subscription


class CustomUserSerializer(UserSerializer):
    avatar = serializers.SerializerMethodField()
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
        # Проверка, подписан ли текущий пользователь на данного пользователя
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Если авторизован, проверяем, есть ли подписка на этого пользователя
            return Subscription.objects.filter(user=request.user, author=obj).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):

    # re_password = serializers.CharField(
    #     style={"input_type": "password"}, write_only=True, required=False
    # )

    class Meta:
        model = FoodgramUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
            # 're_password'
        )

    # def validate(self, attrs):
    #     # Perform validation for password and re_password fields
    #     if attrs["password"] != attrs["re_password"]:
    #         raise serializers.ValidationError("Passwords do not match.")
    #     return attrs

    # def create(self, validated_data):
    #     validated_data.pop(
    #         "re_password"
    #     )  # Remove re_password field before creating the user
    #     return super().create(validated_data)
