from django.contrib import admin

import core.constants as const

from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн форма для добавления ингредиентов к рецепту."""
    model = RecipeIngredient
    extra = 1
    fields = ('ingredient', 'amount', 'measurement_unit_display')
    readonly_fields = ('measurement_unit_display',)
    autocomplete_fields = ('ingredient',)

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
    list_filter = ('tags',)


class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецепта."""
    list_display = (
        'name', 'author', 'pub_date',
        'cooking_time', 'favorited_count'
    )
    search_fields = ('name', 'author__username')
    list_filter = ('pub_date', 'tags')
    inlines = [RecipeIngredientInline, RecipeTagInline]

    fieldsets = (
        (None, {
            'fields': (
                'name', 'author', 'image',
                'text', 'cooking_time'
            )
        }),
    )

    def favorited_count(self, obj):
        """Метод для подсчета общего количества добавлений в избранное."""
        return FavoriteRecipes.objects.filter(recipe=obj).count()

    favorited_count.short_description = const.FAVORITES_ADMIN_TXT


class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингридиентов."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipes)
admin.site.register(ShoppingCart)
