MIN_AMOUNT = 1
MIN_TIME = 1

MEASUREMENT_UNIT_ADMIN_TXT = 'Единица измерения'

VALID_AMOUNT = (
    f'Количество продуктов должно быть не '
    f'менее {MIN_AMOUNT}, указано {{amount}}.'
)
VALID_TIME = (
    f'Минимальное время приготовления {MIN_TIME}'
    f'минута, указано {{cooking_time}}.'
)

VALID_USERNAME = (
    "Логин '{value}' содержит следующие недопустимые символы: "
    "'{invalid_characters}.'"
)

DATA_JOINED = 'Все {name} созданы.'
DATA_FAIL = 'Ошибка при обработке файла {file}: {e}'

INGREDIENTS = 'продукты'
TAGS = 'метки'

USERNAME_VALIDATION_PATTERN = r'[\w.@+-]+'

RECIPE_NOT_FOUND = 'Рецепт с ID {id} не найден.'
