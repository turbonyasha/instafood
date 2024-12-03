from collections import defaultdict
from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

import api.constants as const
from recipes.models import Recipe
from api.serializers import RecipesSubscriptionSerializer


def favorite_or_shopping_cart_action(
        request_method, model, user, recipe_pk, message_text
):
    """Базовая функция для реализации Избранного и Корзины."""
    if not user.is_authenticated:
        raise ValidationError(const.AUTHORIZE_TEXT)
    try:
        recipe = Recipe.objects.get(pk=recipe_pk)
    except Recipe.DoesNotExist:
        raise ValidationError(const.RECIPE_NOT_FOUND)
    if request_method == 'POST':
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(const.RECIPE_ALREADY.format(
                message_text=message_text
            ))
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipesSubscriptionSerializer(
            recipe, context={'user': user}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    get_object_or_404(model, user=user, recipe=recipe).delete()


def get_shoplist_text(in_cart_recipes):
    """Функция для формирования текстового списка покупок."""
    ingredients_summary = defaultdict(int)
    ingredients = {}
    recipes_names = []
    for cart_item in in_cart_recipes:
        recipes_names.append(cart_item.recipe.name)
        for recipe_ingredient in cart_item.recipe.recipe_ingredients.all():
            name = recipe_ingredient.ingredient.name
            ingredients_summary[name] += (
                recipe_ingredient.amount
            )
            if name not in ingredients:
                ingredients[name] = recipe_ingredient.ingredient
    file_header_recipes = ', '.join(recipes_names)
    shopping_list = [const.FILE_HEADER.format(
        file_header=file_header_recipes,
        date=datetime.now().strftime('%Y-%m-%d')
    )]
    for index, (ingredient_name, amount) in enumerate(
        ingredients_summary.items()
    ):
        ingredient = ingredients.get(ingredient_name)
        if ingredient:
            shopping_list.append(
                const.FILE_ROW.format(
                    index=(index + 1),
                    name=ingredient_name.capitalize(),
                    amount=amount,
                    measurement_unit=ingredient.measurement_unit
                )
            )
    return '\n'.join(shopping_list)
