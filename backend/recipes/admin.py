from django.contrib import admin
from .models import Tag, Ingredient, Recipe, RecipeIngredient, FavoriteRecipes, RecipeTag


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн форма для добавления ингредиентов к рецепту."""
    model = RecipeIngredient
    extra = 1  # Количество пустых строк для добавления ингредиентов
    fields = ('ingredient', 'amount', 'measurement_unit_display')  # Поля для отображения в инлайне
    readonly_fields = ('measurement_unit_display',)  # Только для чтения поле с единицей измерения

    def measurement_unit_display(self, obj):
        """Метод для отображения единицы измерения из модели Ingredient."""
        if obj.ingredient and hasattr(obj.ingredient, 'measurement_unit'):
            return obj.ingredient.measurement_unit
        return None  # Если ingredient или measurement_unit нет, возвращаем None

    measurement_unit_display.short_description = 'Единица измерения'  # Заголовок столбца


class RecipeTagInline(admin.TabularInline):
    """Инлайн форма для добавления тегов к рецепту."""
    model = RecipeTag
    extra = 1
    fields = ('tag',)


class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецепта."""
    list_display = ('name', 'author', 'pub_date', 'cooking_time', 'short_link')  # Поля, отображаемые в списке рецептов
    search_fields = ('name', 'author__username')  # Поиск по имени рецепта и имени автора
    list_filter = ('pub_date',)  # Фильтрация по дате публикации
    inlines = [RecipeIngredientInline, RecipeTagInline]  # Добавляем инлайн форму для ингредиентов

    fieldsets = (
        (None, {
            'fields': ('name', 'author', 'image', 'text', 'cooking_time', 'short_link')
        }),
    )


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipes)
