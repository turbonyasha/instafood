import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient

HELP = 'Импорт данных из CSV-файлов для учебного проекта API_YamDB.'
ROW_ERROR = (
    "Неправильное количество столбцов в CSV файле."
    "Ожидаются два столбца: 'name' и 'measurement_unit'."
)


class Command(BaseCommand):
    help = HELP

    def get_row_import_data(self, headers, row, model):
        data = {}
        for header in headers:
            field = model._meta.get_field(header)
            if isinstance(field, models.ForeignKey):
                related_model = field.related_model
                related_object = get_object_or_404(
                    related_model, pk=int(row[headers.index(header)])
                )
                data[header] = related_object
            else:
                data[header] = row[headers.index(field.name)]
        return data

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')
        try:
            with open(path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                headers = next(reader)
                headers = [header.strip() for header in headers]
                print(f"Headers: {headers}")
                if len(headers) != 2:
                    self.stdout.write(self.style.ERROR(ROW_ERROR))
                    return
                for row in reader:
                    data = {
                        'name': row[0].strip(),
                        'measurement_unit': row[1].strip()
                    }
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=data['name'],
                        measurement_unit=data['measurement_unit'],
                        defaults=data
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(
                            f"Создан новый ингредиент: {data['name']}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(
                            f"Ингредиент уже существует: {data['name']}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл {path} не найден."))
