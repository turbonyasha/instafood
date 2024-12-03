from django.contrib import admin
from django_filters import rest_framework as filters
from django.db.models import Count

from recipes.models import Recipe, Tag
from recipes.models import FoodgramUser


class RecipesFilterSet(filters.FilterSet):
    """Расширенный фильтр для поиска по рецептам."""

    author = filters.ModelChoiceFilter(
        queryset=FoodgramUser.objects.all()
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='Рецепт в корзине'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        label='Рецепт в избранных'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
        conjoined=False
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if value is not None:
            if value:
                return recipes.filter(is_in_shopping_cart_annotated=True)
            return recipes.filter(is_in_shopping_cart_annotated=False)
        return recipes

    def filter_is_favorited(self, recipes, name, value):
        if value is not None:
            if value:
                return recipes.filter(is_favorited_annotated=True)
            return recipes.filter(is_favorited_annotated=False)
        return recipes


class UserFilterSet(filters.FilterSet):
    """Расширенный фильтр для поиска по пользователям."""

    is_subscribed = filters.BooleanFilter(
        method='filter_is_subscribed',
        label='Автор в подписках'
    )

    def filter_is_subscribed(self, queryset, name, value):
        user = self.request.user
        if value is not None:
            if value:
                return queryset.filter(subscribers__user=user)
            return queryset.exclude(subscribers__user=user)
        return queryset


class TagFilter(admin.SimpleListFilter):
    """Расширенный фильтр для админки для поиска по тегам."""

    title = 'Метка'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        tags = Tag.objects.all()
        return [(tag.id, tag.name) for tag in tags]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(recipe__tags__id=self.value())
        return queryset


class AuthorFilter(admin.SimpleListFilter):
    title = 'Автор'
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        authors_recipes = Recipe.objects.values('author').annotate(
            recipes_number=Count('author')).filter(recipes_number__gt=0)
        return [(author['author'], FoodgramUser.objects.get(
            id=author['author']
        ).username) for author in authors_recipes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(author__id=self.value())
        return queryset
