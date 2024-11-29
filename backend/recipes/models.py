from django.db import models

import core.validators as valid
from users.models import FoodgramUser


class Tag(models.Model):
    """Модель метки для рецептов."""
    name = models.CharField(
        max_length=64,
        verbose_name='Название',
        null=False,
        blank=False,
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор метки',
        null=False,
        blank=False
    )

    class Meta:
        verbose_name = 'метка'
        verbose_name_plural = 'Метки'
        ordering = ('-id',)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель ингридиентов для рецептов."""
    name = models.CharField(
        max_length=64,
        verbose_name='Название',
        null=False,
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения',
        null=False,
        blank=False
    )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name[:30]} в {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        null=False,
        blank=False
    )
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        null=False,
        blank=False
    )
    image = models.ImageField(
        blank=False,
        verbose_name='Картинка',
        null=False,
        upload_to='recipe/image',
    )
    text = models.TextField(
        verbose_name='Текст',
        null=False,
        blank=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Теги',
        blank=False,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время готовки (мин.)',
        null=False,
        default=1,
        blank=False,
        validators=(valid.validate_cooking_time,)
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    short_link = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Короткая ссылка'
    )
    is_favorited = models.BooleanField(
        default=False,
        verbose_name='В избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
        verbose_name='В списке покупок'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name[:30]}, автор {self.author}'


class RecipeIngredient(models.Model):
    """
    Связующая модель для ингридиентов,
    используемых в рецепте. Содержит поле, определяющее
    количество ингридиентов для рецепта.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(valid.validate_amount,)
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_per_recipe'
            )
        ]

    @classmethod
    def update_or_create_recipeingredient(cls, recipe, ingredient, amount):
        obj, created = cls.objects.update_or_create(
            recipe=recipe,
            ingredient=ingredient,
            defaults={'amount': amount}
        )
        return obj, created

    def __str__(self):
        return (f'{self.amount}{self.ingredient.measurement_unit}'
                f'{self.ingredient} в {self.recipe.name[:20]}')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class BaseRecipeUserModel(models.Model):
    """Базовая модель для связи рецепта с пользователем."""
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} добавил {self.recipe.name[:20]}'


class FavoriteRecipes(BaseRecipeUserModel):
    """
    Связующая модель для составления
    списка рецептов, добавленных пользователем в избранное.
    """
    class Meta(BaseRecipeUserModel.Meta):
        verbose_name = 'рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_recipe_per_user'
            )
        ]


class ShoppingCart(BaseRecipeUserModel):
    """
    Связующая модель для составления
    списка рецептов, добавленных пользователем в корзину покупок.
    """
    class Meta(BaseRecipeUserModel.Meta):
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_in_shopping_cart_per_user'
            )
        ]


class RecipeTag(models.Model):
    """Связующая модель для рецептов и тегов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags',
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_recipes',
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'Теги рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_tag_per_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} - {self.tag.name}'
