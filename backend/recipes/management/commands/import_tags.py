from .base_import import ImportDataBaseCommand

import recipes.constants as const
from recipes.models import Tag


class Command(ImportDataBaseCommand):
    """Команда для импорта тегов."""

    model = Tag
    file_name = const.TAGS_JSON_NAME
    data_name = const.TAGS
