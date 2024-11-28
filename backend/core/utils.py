import random

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

import core.constants as const
from recipes.models import Recipe
from users.serializers import RecipesSubscriptionSerializer


def favorite_or_shopping_cart_action(
        request_method, model, user, recipe_pk, message_text
):
    """Базовая функция для реализации Избранного и Корзины."""
    if not user.is_authenticated:
        return Response(
            {'detail': const.AUTHORIZE_TEXT},
            status=status.HTTP_401_UNAUTHORIZED
        )
    try:
        recipe = Recipe.objects.get(pk=recipe_pk)
    except Recipe.DoesNotExist:
        return Response(
            {'detail': const.RECIPE_NOT_FOUND},
            status=status.HTTP_404_NOT_FOUND
        )
    if request_method == 'POST':
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response({'detail': const.RECIPE_ALREADY.format(
                message_text=message_text
            )}, status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipesSubscriptionSerializer(
            recipe, context={'user': user}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request_method == 'DELETE':
        try:
            model_object = model.objects.get(user=user, recipe=recipe)
            model_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({'detail': const.RECIPE_NOT_IN.format(
                message_text=message_text
            )}, status=status.HTTP_404_NOT_FOUND)


def generate_short_link():
    """Генерация короткой ссылки для рецепта."""
    short_url = ''
    for _ in range(const.SHORT_LINK_LENGHT):
        short_url += random.choice(const.SHORT_LINK_STR)
    return settings.PROJECT_URL + short_url
