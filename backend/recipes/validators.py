import re

from django.core.exceptions import ValidationError

from . import constants as const


def username_validator(value):
    """Валидация для username с регулярным выражением."""
    pattern = const.USERNAME_VALIDATION_PATTERN
    if not re.match(pattern, value):
        raise ValidationError(
            const.VALID_USERNAME.format(
                value=value
            )
        )
