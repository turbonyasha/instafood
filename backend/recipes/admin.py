from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
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
    verbose_name = 'Метка'
    verbose_name_plural = 'Метки'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецепта."""
    list_display = (
        'id', 'name', 'author',
        'cooking_time', 'favorited_count',
        'ingredients_list', 'tags_list', 'image_display'
    )
    search_fields = ('name', 'author__username', 'tags')
    list_filter = [
        'pub_date',
        'tags',
        ('author', admin.RelatedOnlyFieldListFilter)
    ]
    inlines = [RecipeIngredientInline, TagInline]
    filter_vertical = ('ingredients', 'tags')

    fieldsets = (
        (None, {
            'fields': ('name', 'author', 'text', 'cooking_time',)
        }),
        ('КАРТИНКА В РЕЦЕПТЕ', {
            'fields': ('image',)
        }),
    )
    readonly_fields = ('image_display',)

    @admin.display(description='В избранном')
    def favorited_count(self, recipe):
        """Метод для подсчета общего количества добавлений в избранное."""
        return recipe.favoriterecipess.count()

    @mark_safe
    @admin.display(description='Продукты')
    def ingredients_list(self, recipe):
        return '<br>'.join(
            f'{recipe_ingredient.ingredient.name}: '
            f'{recipe_ingredient.amount} '
            f'{recipe_ingredient.ingredient.measurement_unit}'
            for recipe_ingredient in recipe.recipe_ingredients.all()
        )

    @mark_safe
    @admin.display(description='Метки')
    def tags_list(self, recipe):
        """Отображение списка тегов, связанных с рецептом."""
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @mark_safe
    @admin.display(description='Картинка')
    def image_display(self, recipe):
        """Отображение картинки на странице редактирования рецепта."""
        return (
            f'<img src="{recipe.image.url}" '
            f'style="max-width: 150px; max-height: 150px;">'
        ) if recipe.image else ''


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
        'email', 'recipes_count',
        'subscriptions_count', 'followers_count',
        'is_active', 'avatar_display'
    )
    readonly_fields = (
        'recipes_count', 'subscriptions_count',
        'followers_count', 'get_full_name',
        'avatar_display'
    )

    fieldsets = (
        (None, {'fields': ('username',)}),
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
            'fields': ('avatar',)
        }),
    )

    @mark_safe
    @admin.display(description='Аватар')
    def avatar_display(self, user):
        if user.avatar:
            return (
                f'<img src="{user.avatar.url}" '
                f'style="max-width: 150px; max-height: 150px;">'
            )
        return ''

    @mark_safe
    @admin.display(description='Рецептов')
    def recipes_count(self, user):
        count = user.recipes.count()
        return '<a href="{url}?author__id={user_id}">{count}</a>'.format(
            url=reverse('admin:recipes_recipe_changelist'),
            user_id=user.id,
            count=count
        ) if count > 0 else ''

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
    list_display = ('name', 'slug', 'recipes_count')
    search_fields = ('name',)

    @admin.display(description='Рецепты')
    def recipes_count(self, tag):
        return tag.recipes.count()


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
