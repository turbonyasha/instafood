from django.core.exceptions import ValidationError
from . import constants as const


def validate_empty(field):
    """Валидация пустого значения поля на уровне модели."""
    if field is None:
        raise ValidationError(
            const.VALID_EMPTY.format(
                field=field
            )
        )