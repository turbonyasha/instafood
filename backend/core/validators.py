from django.core.exceptions import ValidationError
import core.constants as const


def validate_empty(field):
    """Валидация пустого значения поля на уровне модели."""
    if field is None:
        raise ValidationError(
            const.VALID_EMPTY.format(
                field=field
            )
        )


def validate_amount(amount):
    """Валидация непустого количества на уровне модели."""
    if amount < 1:
        raise ValidationError(
            const.VALID_AMOUNT.format(
                amount=amount
            )
        )


def validate_cooking_time(cooking_time):
    """Валидация непустого времени готовки на уровне модели."""
    if cooking_time < 1:
        raise ValidationError(
            const.VALID_TIME.format(
                cooking_time=cooking_time
            )
        )


def validate_tag_ingredients(
        self, ingredients, tags, image, cooking_time, model
):
    """Валидация тегов и ингридиентов для модели рецептов."""
    for field, field_name in [
        (ingredients.exists(), const.INGREDIENTS),
        (tags.exists(), const.TAGS),
        (image, const.PICTURE),
        (cooking_time and cooking_time > 0, const.COOKING_TIME),
    ]:
        if not field:
            raise ValidationError(
                const.VALID_EMPTY.format(
                    field=field
                )
            )
    for ingredient in ingredients.all():
        if not model.objects.filter(id=ingredient.id).exists():
            raise ValidationError(
                const.VALID_INGREDIENT.format(
                    ingredient=ingredient
                )
            )
    tag_ids = [tag.id for tag in tags.all()]
    ingredient_ids = [ingredient.id for ingredient in ingredients.all()]
    for ids, ids_name in [
        (tag_ids, const.TAGS),
        (ingredient_ids, const.INGREDIENTS)
    ]:
        if len(ids) != len(set(ids)):
            raise ValidationError(
                const.VALID_UNIQUE.format(
                    ids_name=ids_name
                )
            )
