import os

from dotenv import load_dotenv

load_dotenv()
MIN_VALUE = os.getenv('MIN_VALUE', 1)

MEASUREMENT_UNIT_ADMIN_TXT = 'Единица измерения'
FAVORITES_ADMIN_TXT = 'В избранном'

VALID_AMOUNT = (
    f'Количество продуктов должно быть не '
    f'менее {MIN_VALUE}, указано {{amount}}.'
)
VALID_TIME = (
    f'Минимальное время приготовления {MIN_VALUE}'
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

USERNAME_VALIDATION_PATTERN = r'^[\w.@+-]+$'

INGREDIENTS_JSON_NAME = 'ingredients.json'
TAGS_JSON_NAME = 'tags.json'

REDIRECT_RECIPE = '/recipes/{recipe_id}/'
