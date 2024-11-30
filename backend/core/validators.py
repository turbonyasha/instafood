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
