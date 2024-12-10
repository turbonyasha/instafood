import re

from django.core.exceptions import ValidationError

from . import constants as const


def username_validator(username):
    """Валидация для username с регулярным выражением."""
    invalid_characters = ''.join(sorted(set(
        re.findall(
            f'[^{const.USERNAME_VALIDATION_PATTERN}]',
            username
        )
    )))
    if invalid_characters:
        raise ValidationError(
            const.VALID_USERNAME.format(
                value=username,
                invalid_characters=invalid_characters
            ))
