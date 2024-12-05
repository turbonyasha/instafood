from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from . import constants as const
from .models import (
    FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag, FoodgramUser, Subscription
)

user = get_user_model()


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн форма для добавления ингредиентов к рецепту."""
    model = RecipeIngredient
    extra = 1
    fields = ('ingredient', 'amount', 'measurement_unit_display')
    readonly_fields = ('measurement_unit_display',)
    autocomplete_fields = ('ingredient',)

    @admin.display(description=const.MEASUREMENT_UNIT_ADMIN_TXT)
    def measurement_unit_display(self, recipe):
        """Метод для отображения единицы измерения из модели Ingredient."""
        if recipe.ingredient and hasattr(
            recipe.ingredient, 'measurement_unit'
        ):
            return recipe.ingredient.measurement_unit
        return None


class TagInline(admin.TabularInline):
    """Инлайн форма для добавления тегов к рецепту."""
    model = Recipe.tags.through
    extra = 1
    fields = ('tag',)
    list_filter = ('tag',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецепта."""
    list_display = (
        'id', 'name', 'author', 'pub_date',
        'cooking_time', 'favorited_count',
        'ingredients_list', 'tags_list', 'image'
    )
    search_fields = ('name', 'author__username', 'tags')
    list_filter = ('pub_date', 'tags', 'author')
    inlines = [RecipeIngredientInline, TagInline]
    readonly_fields = ('image_preview',)
    filter_vertical = ('ingredients', 'tags')

    fieldsets = (
        (None, {
            'fields': ('name', 'author', 'text', 'cooking_time',)
        }),
        ('КАРТИНКА В РЕЦЕПТЕ', {
            'fields': ('image', 'image_preview',)
        }),
    )

    @admin.display(description=const.FAVORITES_ADMIN_TXT)
    def favorited_count(self, recipe):
        """Метод для подсчета общего количества добавлений в избранное."""
        return recipe.favoriterecipess.count()

    @mark_safe
    @admin.display(description='Продукты')
    def ingredients_list(self, recipe):
        """Отображение списка продуктов, связанных с рецептом."""
        ingredient_info = []
        for ingredient in recipe.ingredients.all():
            recipe_ingredient = ingredient.recipe_ingredients.filter(
                recipe=recipe
            ).first()
            ingredient_info.append(
                f'{ingredient.name}: {recipe_ingredient.amount} '
                f'{ingredient.measurement_unit}'
            )
        return ', '.join(ingredient_info)

    @mark_safe
    @admin.display(description='Метки')
    def tags_list(self, recipe):
        """Отображение списка тегов, связанных с рецептом."""
        return ', '.join(tag.name for tag in recipe.tags.all())

    @mark_safe
    @admin.display(description='Картинка')
    def image_preview(self, recipe):
        """Отображение картинки на странице редактирования рецепта."""
        if recipe.image:
            return (
                f'<img src="{recipe.image.url}" '
                f'style="max-width: 150px; max-height: 150px;">'
            )
        return const.NO_IMAGE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингридиентов."""
    list_display = ('name', 'measurement_unit', 'usage_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', )

    @admin.display(description='В рецептах')
    def usage_count(self, ingredient):
        """Метод для подсчета общего количества добавлений в избранное."""
        return ingredient.recipe_ingredients.count()


@admin.register(FoodgramUser)
class FoodgramUserAdmin(BaseUserAdmin):
    search_fields = ('first_name', 'last_name', 'username', 'email')
    list_display = (
        'username', 'get_full_name',
        'email', 'avatar', 'recipes_count',
        'subscriptions_count', 'followers_count',
        'is_active',
    )
    readonly_fields = (
        'password', 'avatar_preview', 'recipes_count',
        'subscriptions_count', 'followers_count', 'get_full_name'
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ', {'fields': (
            'email', 'get_full_name',
        )}),
        ('РАЗРЕШЕНИЯ', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'user_permissions'
        )}),
        ('СТАТИСТИКА', {'fields': (
            'subscriptions_count', 'followers_count', 'recipes_count',
        )}),
        ('АВАТАР ПОЛЬЗОВАТЕЛЯ', {
            'fields': ('avatar', 'avatar_preview',)
        }),
    )

    @mark_safe
    @admin.display(description='Аватар')
    def avatar_preview(self, user):
        if user.avatar:
            return (
                f'<img src="{user.avatar.url}" '
                f'style="max-width: 150px; max-height: 150px;">'
            )
        return const.NO_IMAGE

    @admin.display(description='Рецептов')
    def recipes_count(self, user):
        return user.recipes_authors.count()

    @admin.display(description='Подписок')
    def subscriptions_count(self, user):
        return user.subscribers.count()

    @admin.display(description='Подписчиков')
    def followers_count(self, user):
        return user.authors.count()

    @admin.display(description='ФИО')
    def get_full_name(self, user):
        return f"{user.first_name} {user.last_name}"


admin.site.register(Subscription)
admin.site.register(Tag)
admin.site.register(FavoriteRecipes)
admin.site.register(ShoppingCart)
admin.site.unregister(Group)
