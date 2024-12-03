from collections import Counter

from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField

import api.constants as const
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
        fields = UserSerializer.Meta.fields + (
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

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
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='author.avatar')

    class Meta(FoodgramUserSerializer.Meta):
        model = Subscription
        fields = FoodgramUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes_count(self, subscribe):
        return subscribe.author.recipes_authors.count()

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
                user=user, recipe=recipe).exists()
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


class RecipeIngredientWriteSerializer(
    RecipeIngredientRetriveSerializer
):
    """Сериализатор для создания и обновления связи рецепта и ингридиента."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1)]
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
        validators=[MinValueValidator(1)]
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, attrs):
        ingredients = attrs.get('ingredients', [])
        tags = attrs.get('tags', [])
        image = attrs.get('image', [])
        for field, field_name in [
            (ingredients, const.INGREDIENTS),
            (tags, const.TAGS),
        ]:
            if field is None or (isinstance(field, list) and not field):
                raise serializers.ValidationError(
                    const.VALID_EMPTY.format(field=field_name)
                )
        if image in [None, '']:
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
                            ).items() if into > const.DEFAULT_ONE
                        ]
                    )
                )
        return attrs

    def _create_or_update_ingredients(self, recipe, ingredients_data):
        ingredients_to_create = []
        ingredients_to_update = []
        existing_ingredients = {
            (recipe.ingredient.id): recipeigredient
            for recipeigredient in RecipeIngredient.objects.filter(
                recipe=recipe
            )
        }
        for ingredient_data in ingredients_data:
            id = ingredient_data['id']
            amount = ingredient_data['amount']
            if id in existing_ingredients:
                recipe_ingredient = existing_ingredients[id]
                recipe_ingredient.amount = amount
                ingredients_to_update.append(recipe_ingredient)
            else:
                ingredients_to_create.append(RecipeIngredient(
                    recipe=recipe,
                    ingredient=id,
                    amount=amount
                ))
        if ingredients_to_create:
            RecipeIngredient.objects.bulk_create(ingredients_to_create)
        if ingredients_to_update:
            RecipeIngredient.objects.bulk_update(
                ingredients_to_update, ['amount']
            )

    def create(self, validated_data):
        recipe = super().create(validated_data)
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        self._create_or_update_ingredients(
            recipe=recipe, ingredients_data=ingredients_data
        )
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        self.validate(validated_data)
        instance = super().update(instance, validated_data)
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
            context=self.context
        ).data
