from collections import Counter

from django.core.validators import MinValueValidator
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

import api.constants as const
from recipes.models import (
    FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag, FoodgramUser, Subscription
)
from recipes.constants import MIN_AMOUNT, MIN_TIME


class FoodgramUserSerializer(UserSerializer):
    """Сериализатор для чтения пользователя."""
    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = (
            *UserSerializer.Meta.fields,
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, user):
        user = self.context['request'].user
        return (
            user.is_authenticated and Subscription.objects.filter(
                user=user,
                author=user
            ).exists()
        )


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


class SubscriptionSerializer(FoodgramUserSerializer):
    """Сериализатор для чтения подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta(FoodgramUserSerializer.Meta):
        model = FoodgramUser
        fields = (
            *FoodgramUserSerializer.Meta.fields,
            'recipes', 'recipes_count'
        )

    def get_recipes(self, user):
        return RecipesSubscriptionSerializer(
            Recipe.objects.filter(
                author=user
            )[:int(self.context.get('request').GET.get(
                'recipes_limit', 10**10
            ))],
            many=True).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор продуктов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientRetriveSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения связи рецепта и продукта."""
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
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = FoodgramUserSerializer()
    ingredients = RecipeIngredientRetriveSerializer(
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

    def _get_is_in_user_list(self, recipe, model):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and model.objects.filter(
                user=user, recipe=recipe
            ).exists()
        )

    def get_is_favorited(self, recipe):
        return self._get_is_in_user_list(
            recipe=recipe,
            model=FavoriteRecipes
        )

    def get_is_in_shopping_cart(self, recipe):
        return self._get_is_in_user_list(
            recipe=recipe,
            model=ShoppingCart
        )


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления связи рецепта и продукта."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, удаления, редактирования рецептов."""
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientWriteSerializer(
        many=True, required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(MIN_TIME)]
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, attrs):
        ingredients = attrs.get('ingredients', [])
        tags = attrs.get('tags', [])
        image = attrs.get('image', [])
        for field, field_name in [
            (ingredients, const.INGREDIENTS),
            (tags, const.TAGS),
        ]:
            if not field:
                raise serializers.ValidationError(
                    const.VALID_EMPTY.format(field=field_name)
                )
        if not image:
            raise serializers.ValidationError(
                const.VALID_EMPTY.format(field=const.PICTURE)
            )
        for ids, ids_name in [
            ([tag.id for tag in tags], const.TAGS),
            ([
                ingredient['id'] for ingredient in ingredients
            ], const.INGREDIENTS)
        ]:
            if len(ids) != len(set(ids)):
                raise serializers.ValidationError(
                    const.VALID_UNIQUE.format(
                        ids_name=ids_name, duplicates=[
                            id for id, into in Counter(
                                ids
                            ).items() if into > 1
                        ]
                    )
                )
        return attrs

    def _create_ingredients(self, recipe, ingredients_data):
        recipe.recipe_ingredients.all().delete()
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = super().create(validated_data)
        self._create_ingredients(
            recipe=recipe, ingredients_data=ingredients_data
        )
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        self.validate(validated_data)
        ingredients_data = validated_data.pop('ingredients')
        self._create_ingredients(instance, ingredients_data)
        instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeRetriveSerializer(
            instance,
            context=self.context
        ).data
