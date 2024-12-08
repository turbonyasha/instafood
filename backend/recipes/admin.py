from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from . import constants as const
from .models import (
    FavoriteRecipes, FoodgramUser, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Subscription, Tag
)

user = get_user_model()


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн форма для добавления продуктов к рецепту."""
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
    filter_vertical = ('ingredients', 'tags')
    readonly_fields = ('image_preview',)

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
        ingredient_info = [
            f'{recipe_ingredient.ingredient.name}: '
            f'{recipe_ingredient.amount} '
            f'{recipe_ingredient.ingredient.measurement_unit}'
            for recipe_ingredient in recipe.recipe_ingredients.all()
        ]
        return '<br>'.join(ingredient_info)

    @mark_safe
    @admin.display(description='Метки')
    def tags_list(self, recipe):
        """Отображение списка тегов, связанных с рецептом."""
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @mark_safe
    @admin.display(description='Картинка')
    def image_preview(self, recipe):
        """Отображение картинки на странице редактирования рецепта."""
        if recipe.image:
            return (
                f'<img src="{recipe.image.url}" '
                f'style="max-width: 150px; max-height: 150px;">'
            )
        return ''


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для продуктов."""
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
        return ''

    @admin.display(description='Рецептов')
    def recipes_count(self, user):
        count = user.recipes.count()
        if count > 0:
            url = reverse('admin:recipes_recipe_changelist')
            filter_url = f"{url}?author__id={user.id}"
            return format_html('<a href="{}">{}</a>', filter_url, count)
        return count

    @admin.display(description='Подписок')
    def subscriptions_count(self, user):
        return user.subscribers.count()

    @admin.display(description='Подписчиков')
    def followers_count(self, user):
        return user.authors.count()

    @admin.display(description='ФИО')
    def get_full_name(self, user):
        return f'{user.first_name} {user.last_name}'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для меток."""
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для подписок."""
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user',)


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    """Админка для избранного."""
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для корзины."""
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)


admin.site.unregister(Group)
