import json
import os

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import models

import recipes.constants as const
from recipes.models import Ingredient, Tag

HELP = 'Импорт данных из JSON файлов'


class Command(BaseCommand):
    help = HELP

    def get_row_import_data(self, row, model):
        data = {}
        for key, value in row.items():
            try:
                field = model._meta.get_field(key)
                if isinstance(field, models.ForeignKey):
                    model = field.model
                    object_model = get_object_or_404(
                        model, pk=int(value)
                    )
                    data[key] = object_model
                else:
                    data[key] = value
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Ошибка при обработке поля {key}: {str(e)}'
                ))
                continue
        return data

    def handle(self, *args, **options):
        ingredient_file_path = os.path.join(
            settings.BASE_DIR, 'data', 'ingredients.json'
        )
        tag_file_path = os.path.join(
            settings.BASE_DIR, 'data', 'tags.json'
        )
        for file, model in [
            (ingredient_file_path, Ingredient),
            (tag_file_path, Tag)
        ]:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    data = []
                    for row in file_data:
                        row_data = self.get_row_import_data(row, model)
                        data.append(Ingredient(**row_data))
                    try:
                        model.objects.bulk_create(data)
                        self.stdout.write(self.style.SUCCESS(
                            const.DATA_JOINED.format(
                                name=data['name']
                            )))
                    except IntegrityError:
                        self.stdout.write(self.style.ERROR(const.DATA_FAIL))
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(
                    const.FAIL_FAIL.format(
                        file=file
                    )))
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(
                    const.JSON_FAIL.format(
                        file=file
                    )))
