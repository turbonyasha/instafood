import json
import os

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.conf import settings

import recipes.constants as const
from recipes.models import Ingredient, Tag

HELP = 'Импорт данных из JSON файлов'


class Command(BaseCommand):
    help = HELP

    def handle(self, *args, **options):
        file_paths = [
            (
                os.path.join(settings.BASE_DIR, 'data', 'ingredients.json'),
                Ingredient, const.INGREDIENTS
            ),
            (
                os.path.join(settings.BASE_DIR, 'data', 'tags.json'),
                Tag, const.TAGS
            ),
        ]
        for file, model, name in file_paths:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    data = [model(**row) for row in file_data]
                    model.objects.bulk_create(data, ignore_conflicts=True)
                    self.stdout.write(self.style.SUCCESS(
                        const.DATA_JOINED.format(
                            name=name
                        )
                    ))
            except (FileNotFoundError, json.JSONDecodeError) as e:
                self.stdout.write(self.style.ERROR(
                    const.FORMAT_FAIL.format(
                        file=file,
                        e=str(e)
                    )
                ))
            except IntegrityError:
                self.stdout.write(self.style.ERROR(const.DATA_FAIL))
