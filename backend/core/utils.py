from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import random
from django.conf import settings
from rest_framework.pagination import PageNumberPagination

import core.constants as const


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для преобразования base64 в изображение."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def generate_short_link():
    """Генерация короткой ссылки для рецепта."""
    short_url = ''
    for _ in range(const.SHORT_LINK_LENGHT):
        short_url += random.choice(const.SHORT_LINK_STR)
    return settings.PROJECT_URL + short_url


class LimitPageNumberPagination(PageNumberPagination):
    """Кастомная пагинация с измененным наименованием параметра."""
    page_size = 6
    page_size_query_param = 'limit'
