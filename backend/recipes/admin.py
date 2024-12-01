from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from . import constants as const

from .models import (
    FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
    RecipeTag, ShoppingCart, Tag, FoodgramUser, Subscription
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


class RecipeTagInline(admin.TabularInline):
    """Инлайн форма для добавления тегов к рецепту."""
    model = RecipeTag
    extra = 1
    fields = ('tag',)
    list_filter = ('tags',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецепта."""
    list_display = (
        'id', 'name', 'author', 'pub_date',
        'cooking_time', 'favorited_count',
        'ingredients_list', 'tags_list', 'image'
    )
    search_fields = ('name', 'author__username')
    list_filter = ('pub_date', 'tags')
    inlines = [RecipeIngredientInline, RecipeTagInline]
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
        return FavoriteRecipes.objects.filter(recipe=recipe).count()

    @mark_safe
    @admin.display(description='Продукты')
    def ingredients_list(self, recipe):
        """Отображаем список продуктов, связанных с рецептом."""
        return mark_safe(', '.join([
            ingredient.name for ingredient in recipe.ingredients.all()
        ]))

    @mark_safe
    @admin.display(description='Метки')
    def tags_list(self, recipe):
        """Отображаем список тегов, связанных с рецептом."""
        tags = recipe.tags.all()
        return mark_safe(', '.join([tag.name for tag in tags]))

    @mark_safe
    @admin.display(description='Текущая картинка рецепта')
    def image_preview(self, recipe):
        """Отображаем изображение на странице редактирования рецепта."""
        if recipe.image:
            return mark_safe(
                f'<img src="{recipe.image.url}" '
                f'style="max-width: 150px; max-height: 150px;">'
            )
        return 'Нет изображения'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингридиентов."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class FoodgramUserAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'username', 'email')

    fieldsets = (
        (None, {
            'fields': '__all__'
        }),
        ('АВАТАР ПОЛЬЗОВАТЕЛЯ', {
            'fields': ('avatar', 'avatar_preview',)
        }),
    )

    @mark_safe
    def avatar_preview(self, user):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}" style="max-width: 150px; max-height: 150px;">')
        return 'Нет изображения'


admin.site.register(FoodgramUser)
admin.site.register(Subscription)
admin.site.register(Tag)
admin.site.register(FavoriteRecipes)
admin.site.register(ShoppingCart)
admin.site.unregister(Group)
