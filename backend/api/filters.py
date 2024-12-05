from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag, FoodgramUser


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
        if value:
            return recipes.filter(is_in_shopping_cart_annotated=True)
        return recipes

    def filter_is_favorited(self, recipes, name, value):
        if value:
            return recipes.filter(is_favorited_annotated=True)
        return recipes


class UserFilterSet(filters.FilterSet):
    """Расширенный фильтр для поиска по пользователям."""

    is_subscribed = filters.BooleanFilter(
        method='filter_is_subscribed',
        label='Автор в подписках'
    )

    def filter_is_subscribed(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.exclude(subscribers__user=user)
        return queryset
