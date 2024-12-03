from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from . import constants as const
from .models import (
    FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag, FoodgramUser, Subscription
)
from api.filters import AuthorFilter, TagFilter

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
    list_filter = (TagFilter,)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецепта."""
    list_display = (
        'id', 'name', 'author', 'pub_date',
        'cooking_time', 'favorited_count',
        'ingredients_list', 'tags_list', 'image'
    )
    search_fields = ('name', 'author__username')
    list_filter = ('pub_date', TagFilter, AuthorFilter)
    inlines = [RecipeIngredientInline, TagInline]
    readonly_fields = ('image_preview',)

    fieldsets = (
        (None, {
            'fields': ('name', 'author', 'text', 'cooking_time',)
        }),
        ('КАРТИНКА В РЕЦЕПТЕ', {
            'fields': ('image', 'image_preview',)
        }),
    )

    def get_author_filter(self, request):
        authors = Recipe.objects.values_list('author', flat=True).distinct()
        return [(
                author.id,
                author.get_full_name()
                ) for author in FoodgramUser.objects.filter(id__in=authors)]

    @admin.display(description=const.FAVORITES_ADMIN_TXT)
    def favorited_count(self, recipe):
        """Метод для подсчета общего количества добавлений в избранное."""
        return recipe.favoriterecipess.count()

    @mark_safe
    @admin.display(description='Продукты')
    def ingredients_list(self, recipe):
        """Отображение списка продуктов, связанных с рецептом."""
        return mark_safe(', '.join([
            ingredient.name for ingredient in recipe.ingredients.all()
        ]))

    @mark_safe
    @admin.display(description='Метки')
    def tags_list(self, recipe):
        """Отображение списка тегов, связанных с рецептом."""
        tags = recipe.tags.all()
        return mark_safe(', '.join([tag.name for tag in tags]))

    @mark_safe
    @admin.display(description='Текущая картинка рецепта')
    def image_preview(self, recipe):
        """Отображение картинки на странице редактирования рецепта."""
        if recipe.image:
            return mark_safe(
                f'<img src="{recipe.image.url}" '
                f'style="max-width: 150px; max-height: 150px;">'
            )
        return const.NO_IMAGE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингридиентов."""
    list_display = ('name', 'measurement_unit', 'usage_count')
    search_fields = ('name',)

    @admin.display(description='Использование в рецептах')
    def usage_count(self, recipe):
        """Метод для подсчета общего количества добавлений в избранное."""
        return recipe.recipe_ingredients.count()


@admin.register(FoodgramUser)
class FoodgramUserAdmin(BaseUserAdmin):
    search_fields = ('first_name', 'last_name', 'username', 'email')
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    readonly_fields = ('password', 'avatar_preview')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ', {'fields': (
            'first_name', 'last_name', 'email'
        )}),
        ('РАЗРЕШЕНИЯ', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'user_permissions'
        )}),
        ('СТАТИСТИКА', {'fields': ('last_login', 'date_joined')}),
        ('АВАТАР ПОЛЬЗОВАТЕЛЯ', {
            'fields': ('avatar', 'avatar_preview',)
        }),
    )

    @mark_safe
    def avatar_preview(self, user):
        if user.avatar:
            return mark_safe(
                f'<img src="{user.avatar.url}" '
                f'style="max-width: 150px; max-height: 150px;">'
            )
        return const.NO_IMAGE


admin.site.register(Subscription)
admin.site.register(Tag)
admin.site.register(FavoriteRecipes)
admin.site.register(ShoppingCart)
admin.site.unregister(Group)
