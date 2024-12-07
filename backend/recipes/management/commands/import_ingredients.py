from .base_import import ImportDataBaseCommand

import recipes.constants as const
from recipes.models import Ingredient


class Command(ImportDataBaseCommand):
    """Команда для импорта продуктов."""

    model = Ingredient
    file_name = const.INGREDIENTS_JSON_NAME
    data_name = const.INGREDIENTS
