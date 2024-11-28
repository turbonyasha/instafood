from django_filters import rest_framework as filters
from django.contrib import admin

from recipes.models import Recipe, Tag
from users.models import FoodgramUser


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
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Теги'
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value is not None:
            if value:
                return queryset.filter(is_in_shopping_cart_annotated=True)
            return queryset.filter(is_in_shopping_cart_annotated=False)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value is not None:
            if value:
                return queryset.filter(is_favorited_annotated=True)
            return queryset.filter(is_favorited_annotated=False)
        return queryset


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
