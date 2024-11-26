from django.core.exceptions import ValidationError


def validate_empty(field):
    """Валидация пустого значения поля на уровне модели."""
    if field is None:
        raise ValidationError(
            f'Поле {field} не должно быть пустым!'
        )


def validate_amount(amount):
    """Валидация непустого количества на уровне модели."""
    if amount < 1:
        raise ValidationError(
            f'Количество ингридиентов должно'
            f'быть не менее 1, указано {amount}.'
        )


def validate_cooking_time(cooking_time):
    """Валидация непустого времени готовки на уровне модели."""
    if cooking_time < 1:
        raise ValidationError(
            f'Минимальное время приготовления'
            f'1 минута, указано {cooking_time}.'
        )
    
