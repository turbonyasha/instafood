from collections import Counter

from django.core.validators import MinValueValidator
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

import api.constants as const
from foodgram.settings import DEFAULT
from recipes.models import (
    FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag, FoodgramUser, Subscription
)


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

    def get_is_subscribed(self, subscription):
        user = self.context['request'].user
        if user.is_authenticated:
            if isinstance(subscription, Subscription):
                return Subscription.objects.filter(
                    user=user, author=subscription.author
                ).exists()
            return Subscription.objects.filter(
                user=user, author=subscription
            ).exists()
        return False


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


class SubscribtionSerializer(FoodgramUserSerializer):
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(required=False)
    avatar = serializers.ImageField(source='author.avatar')

    class Meta(FoodgramUserSerializer.Meta):
        model = Subscription
        fields = FoodgramUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']
        if user == author:
            raise serializers.ValidationError(const.SUBSCRIBTION_MYSELF)
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(const.SUBSCRIBTION_ALREADY)
        return data

    def get_recipes_count(self, author):
        return author.recipes_count

    def get_recipes(self, obj):
        return RecipesSubscriptionSerializer(
            Recipe.objects.filter(
                author=obj.author
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
    """Сериализатор ингридиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientRetriveSerializer(serializers.ModelSerializer):
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
    """Сериализатор для создания и обновления связи рецепта и ингридиента."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=[MinValueValidator(DEFAULT)]
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
        validators=[MinValueValidator(DEFAULT)]
    )

    class Meta:
        model = Recipe
        fields = '__all__'

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
                        ids_name=ids_name, duplicates=[
                            id for id, into in Counter(
                                ids
                            ).items() if into > 1
                        ]
                    )
                )
        return attrs

    def _create_or_update_ingredients(self, recipe, ingredients_data):
        ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=Ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        if ingredients:
            RecipeIngredient.objects.bulk_update(
                ingredients,
                ignore_conflicts=True
            )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = super().create(validated_data)
        self._create_or_update_ingredients(
            recipe=recipe, ingredients_data=ingredients_data
        )
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        self.validate(validated_data)
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            self._create_or_update_ingredients(instance, ingredients_data)
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeRetriveSerializer(
            instance,
            context=self.context
        ).data
