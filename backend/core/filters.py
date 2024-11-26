from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget
from recipes.models import Recipe, FavoriteRecipes, ShoppingCart
from users.models import FoodgramUser


class RecipesFilterSet(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=FoodgramUser.objects.all())
    
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='Рецепт в корзине'
    )

    # Фильтр для поля is_favorited_annotated
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        label='Рецепт в избранных'
    )
    # Фильтр по тегам (несколько тегов через slug)
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Теги'
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value is not None:
            if value:  # Если значение True, фильтруем рецепты, которые в корзине
                return queryset.filter(is_in_shopping_cart_annotated=True)
            else:  # Если значение False, исключаем рецепты, которые в корзине
                return queryset.filter(is_in_shopping_cart_annotated=False)
        return queryset  # Если фильтр не задан, возвращаем весь queryset

    # Метод для фильтрации по избранному
    def filter_is_favorited(self, queryset, name, value):
        if value is not None:
            if value:  # Если значение True, фильтруем рецепты, которые в избранном
                return queryset.filter(is_favorited_annotated=True)
            else:  # Если значение False, исключаем рецепты, которые в избранном
                return queryset.filter(is_favorited_annotated=False)
        return queryset


class UserFilterSet(filters.FilterSet):
    is_subscribed = filters.BooleanFilter(
        method='filter_is_subscribed',
        label='Рецепт в корзине'
    )

    def filter_is_subscribed(self, queryset, name, value):
        user = self.request.user
        if value is not None:
            if value:  # Если значение True, фильтруем пользователей, на которых подписан текущий пользователь
                return queryset.filter(subscribers__user=user)
            else:  # Если False, исключаем тех, на кого подписан текущий пользователь
                return queryset.exclude(subscribers__user=user)
        return queryset