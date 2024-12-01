from django.shortcuts import get_object_or_404
from rest_framework import serializers

import core.constants as const
from core.models import Base64ImageField
from users.serializers import CustomUserSerializer

from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения связи рецепта и ингридиента."""
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeRetriveSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = CustomUserSerializer()
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return FavoriteRecipes.objects.filter(
                user=user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user, recipe=obj
            ).exists()
        return False


class RecipeIngredientCreateUpdateSerializer(RecipeIngredientSerializer):
    """Сериализатор для создания и обновления связи рецепта и ингридиента."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                const.VALID_INGREDIENT.format(
                    amount=value
                )
            )
        return value


class RecipeCUDSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, удаления, редактирования рецептов."""
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientCreateUpdateSerializer(
        many=True, required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, attrs):
        cooking_time = attrs.get('cooking_time', None)
        ingredients = attrs.get('ingredients', [])
        tags = attrs.get('tags', [])
        image = attrs.get('image', None)
        for field, field_name in [
            (ingredients, const.INGREDIENTS),
            (tags, const.TAGS),
            (image, const.PICTURE),
            (cooking_time and cooking_time > 0, const.COOKING_TIME),
        ]:
            if field is None or (isinstance(field, list) and not field):
                raise serializers.ValidationError(
                    const.VALID_EMPTY.format(field=field_name)
                )
        if cooking_time is not None and cooking_time <= 0:
            raise serializers.ValidationError(
                const.VALID_EMPTY.format(field=const.COOKING_TIME)
            )
        if image is None:
            if 'image' in attrs:
                raise serializers.ValidationError(
                    const.VALID_EMPTY.format(field=const.PICTURE)
                )
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    const.VALID_INGREDIENT.format(ingredient=ingredient)
                )
        tag_ids = [tag.id for tag in tags]
        ingredient_ids = [
            ingredient['id'] for ingredient in ingredients
        ]
        for ids, ids_name in [
            (tag_ids, const.TAGS),
            (ingredient_ids, const.INGREDIENTS)
        ]:
            if len(ids) != len(set(ids)):
                raise serializers.ValidationError(
                    const.VALID_UNIQUE.format(
                        ids_name=ids_name
                    )
                )
        return attrs

    def _create_or_update_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_data['id']
            )
            recipe_ingredient, created = (
                RecipeIngredient.update_or_create_recipeingredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                ))
            recipe_ingredient.save()

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self._create_or_update_ingredients(
            recipe=recipe, ingredients_data=ingredients_data
        )
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        self.validate(validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            self._create_or_update_ingredients(instance, ingredients_data)
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeRetriveSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data
