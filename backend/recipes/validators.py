import re

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


def username_validator(value):
    """Валидация для username с регулярным выражением."""
    regex = r'[\w.@+-]'
    if not re.match(regex, value):
        raise ValidationError(
            const.VALID_USERNAME.format(
                value=value
            )
        )
