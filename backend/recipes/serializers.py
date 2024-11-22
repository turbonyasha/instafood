from rest_framework import serializers, exceptions
from django.shortcuts import get_object_or_404

from .models import Tag, Recipe, Ingredient, RecipeIngredient
from users.models import FoodgramUser

from .utils import Base64ImageField
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
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
    is_favorited = serializers.BooleanField(
        read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True)
    # SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')


class RecipeIngredientCreateUpdateSerializer(RecipeIngredientSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCUDSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeIngredientCreateUpdateSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')  # Извлекаем ингредиенты
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)  # Создаем рецепт
        print(ingredients_data)
    # Создаем ингредиенты для рецепта через модель RecipeIngredient
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['id']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient),
                amount=amount
            )

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data['id']
                amount = ingredient_data['amount']
                recipe_ingredient, created = RecipeIngredient.objects.get_or_create(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient, id=ingredient_id)
                )
                recipe_ingredient.amount = amount
                recipe_ingredient.save()
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