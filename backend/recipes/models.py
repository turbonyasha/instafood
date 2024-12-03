from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator

from . import constants as const
from .validators import username_validator


class FoodgramUser(AbstractUser):
    """Модель пользователя с дополнительным
    полем аватарки и подписки."""

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        unique=True,
        max_length=254)
    first_name = models.CharField(
        verbose_name='Имя',
        blank=False,
        null=False,
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        blank=False,
        null=False,
        max_length=150
    )
    avatar = models.ImageField(
        blank=True,
        null=True,
        verbose_name='Аватар',
        upload_to='avatar/image'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель для подписок пользователя."""
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribers',  # subscriptions
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='authors',  # subscribers
        null=True,
        verbose_name='Автор рецептов'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author_in_subscriptions'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Tag(models.Model):
    """Модель метки для рецептов."""
    name = models.CharField(
        max_length=32,
        verbose_name='Название',
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        max_length=32,
    )

    class Meta:
        verbose_name = 'метка'
        verbose_name_plural = 'Метки'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель продуктов для рецептов."""
    name = models.CharField(
        max_length=128,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Мера измерения',
    )

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_per_measurment_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецептов."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        null=False,
        blank=False,
        related_name='recipes_authors'
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
        verbose_name='Теги',
        related_name='recipes_tags'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время готовки (мин.)',
        null=False,
        default=const.DEFAULT_TIME,
        blank=False,
        validators=(MinValueValidator(1),)
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    # is_favorited = models.BooleanField(
    #     default=False,
    #     verbose_name='В избранном'
    # )
    # is_in_shopping_cart = models.BooleanField(
    #     default=False,
    #     verbose_name='В списке покупок'
    # )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name[:30]}, автор {self.author}'

    def get_absolute_url(self):
        return reverse('recipes-detail', args=[self.pk])


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
        validators=(MinValueValidator(1),)
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'продукт в рецепте'
        verbose_name_plural = 'Продукты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_per_recipe'
            )
        ]

    # @classmethod
    # def update_or_create_recipeingredient(cls, recipe, ingredient, amount):
    #     obj, created = cls.objects.update_or_create(
    #         recipe=recipe,
    #         ingredient=ingredient,
    #         defaults={'amount': amount}
    #     )
    #     return obj, created

    def __str__(self):
        return (f'{self.amount} {self.ingredient.measurement_unit} '
                f'{self.ingredient} в {self.recipe.name[:20]}')

    # def save(self, *args, **kwargs):
    #     self.clean()
    #     super().save(*args, **kwargs)


class BaseRecipeUserModel(models.Model):
    """Базовая модель для связи рецепта с пользователем."""
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_%(class)s_recipe_per_user'
            )
        ]

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


class ShoppingCart(BaseRecipeUserModel):
    """
    Связующая модель для составления
    списка рецептов, добавленных пользователем в корзину покупок.
    """
    class Meta(BaseRecipeUserModel.Meta):
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'


# class RecipeTag(models.Model):
#     """Связующая модель для рецептов и тегов."""
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#         related_name='recipe_tags',
#         verbose_name='Рецепт'
#     )
#     tag = models.ForeignKey(
#         Tag,
#         on_delete=models.CASCADE,
#         related_name='tag_recipes',
#         verbose_name='Тег'
#     )

#     class Meta:
#         verbose_name = 'тег рецепта'
#         verbose_name_plural = 'Теги рецептов'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['recipe', 'tag'],
#                 name='unique_tag_per_recipe'
#             )
#         ]

#     def __str__(self):
#         return f'{self.recipe.name}, метка {self.tag.name}'
