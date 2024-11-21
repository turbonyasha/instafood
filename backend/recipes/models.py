from django.db import models

from users.models import FoodgramUser


class Tag(models.Model):
    """Модель метки для рецептов."""
    # добавить related_name
    name = models.CharField(
        max_length=64,
        verbose_name='Название',
        null=False,
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор метки',
        null=False
    )

    class Meta:
        verbose_name = 'метка'
        verbose_name_plural = 'Метки'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель ингридиентов для рецептов."""
    # добавить related_name
    name = models.CharField(
        max_length=64,
        verbose_name='Название',
        null=False,
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения',
        null=False,
    )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name[:30]


class Recipe(models.Model):
    """Модель рецептов."""
    # добавить related_name
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
        blank=True,
        verbose_name='Картинка',
        null=True
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
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Теги',
        blank=False
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        null=False,
        default=0,
        blank=False
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:30]


class RecipeIngredient(models.Model):
    """
    Связующая модель для ингридиентов,
    используемых в рецепте. Содержит поле, определяющее
    количество ингридиентов для рецепта.
    """
    # добавить related_name
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
    amount = models.IntegerField(
        verbose_name='Количество'
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return (f'{self.amount}{self.ingredient.measurement_unit}'
                f'{self.ingredient} в {self.recipe.name[:20]}')


class FavoriteRecipes(models.Model):
    """
    Связующая модель для составления
    списка рецептов, добавленных пользователем в избранное.
    """
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    # почитать про класс-методы в таких случаях, не забыть про
    # валидацию в сериализаторах и формах
    # @classmethod
    # def add_to_favorites(cls, user, recipe):
    #     return cls.objects.get_or_create(user=user, recipe=recipe)

    # @classmethod
    # def remove_from_favorites(cls, user, recipe):
    #     return cls.objects.filter(user=user, recipe=recipe).delete()

    class Meta:
        verbose_name = 'рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f'{self.user} добавил {self.recipe[:20]} в избранное'


class RecipeTag(models.Model):
    """Промежуточная модель для связи рецептов и тегов."""
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
        unique_together = ('recipe', 'tag')

    def __str__(self):
        return f'{self.recipe.name} - {self.tag.name}'
