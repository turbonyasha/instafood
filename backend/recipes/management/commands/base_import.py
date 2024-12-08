import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError

import recipes.constants as const

HELP = 'Импорт данных из JSON файлов'


class ImportDataBaseCommand(BaseCommand):
    """Общий базовый класс для импорта данных в базу."""

    model = None
    file_name = None
    data_name = None

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', self.file_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.model.objects.bulk_create(
                    [self.model(**row) for row in json.load(f)],
                    ignore_conflicts=True
                )
                self.stdout.write(self.style.SUCCESS(
                    const.DATA_JOINED.format(name=self.data_name)
                ))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.stdout.write(self.style.ERROR(
                const.DATA_FAIL.format(file=file_path, e=str(e))
            ))
        except IntegrityError:
            self.stdout.write(self.style.ERROR(const.DATA_FAIL))
