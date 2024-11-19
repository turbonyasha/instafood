from rest_framework import serializers, exceptions

from .models import FoodgramUser


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=False)

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
