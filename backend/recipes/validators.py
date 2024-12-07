import re

from django.core.exceptions import ValidationError

from . import constants as const


def username_validator(username):
    """Валидация для username с регулярным выражением."""
    pattern = const.USERNAME_VALIDATION_PATTERN
    invalid_characters = [
        char for char in username if not re.match(pattern, char)
    ]

    if invalid_characters:
        invalid_chars_str = ', '.join(invalid_characters)
        raise ValidationError(
            const.VALID_USERNAME.format(
                value=username,
                invalid_characters=invalid_chars_str
            )
        )
