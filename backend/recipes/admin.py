from django.contrib import admin

from .models import (
    Tag, Ingredient, Recipe, RecipeIngredient,
    FavoriteRecipes, RecipeTag, ShoppingCart
)
import core.constants as const


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн форма для добавления ингредиентов к рецепту."""
    model = RecipeIngredient
    extra = 1
    fields = ('ingredient', 'amount', 'measurement_unit_display')
    readonly_fields = ('measurement_unit_display',)

    def measurement_unit_display(self, obj):
        """Метод для отображения единицы измерения из модели Ingredient."""
        if obj.ingredient and hasattr(obj.ingredient, 'measurement_unit'):
            return obj.ingredient.measurement_unit
        return None

    measurement_unit_display.short_description = (
        const.MEASUREMENT_UNIT_ADMIN_TXT
    )


class RecipeTagInline(admin.TabularInline):
    """Инлайн форма для добавления тегов к рецепту."""
    model = RecipeTag
    extra = 1
    fields = ('tag',)


class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецепта."""
    list_display = ('name', 'author', 'pub_date', 'cooking_time', 'short_link')
    search_fields = ('name', 'author__username')
    list_filter = ('pub_date',)
    inlines = [RecipeIngredientInline, RecipeTagInline]

    fieldsets = (
        (None, {
            'fields': (
                'name', 'author', 'image',
                'text', 'cooking_time', 'short_link'
            )
        }),
    )


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipes)
admin.site.register(ShoppingCart)
