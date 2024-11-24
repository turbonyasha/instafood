import re

from django.core.exceptions import ValidationError


def validate_empty(field):
    if field is None:
        raise ValidationError(
            f'Поле {field} не должно быть пустым!'
        )


def validate_amount(amount):
    if amount < 1:
        raise ValidationError(
            f'Количество ингридиентов должно быть не менее 1, указано {amount}.'
        )


def validate_cooking_time(cooking_time):
    if cooking_time < 1:
        raise ValidationError(
            f'Минимальное время приготовления 1 минута, указано {cooking_time}.'
        )
    
