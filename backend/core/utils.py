from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import random
from django.conf import settings
from rest_framework.pagination import PageNumberPagination

SHORT_LINK_LENGHT = 10
SHORT_LINK_STR = 'qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def generate_short_link():
    short_url = ''
    for _ in range(SHORT_LINK_LENGHT):
        short_url += random.choice(SHORT_LINK_STR)
    return settings.PROJECT_URL + short_url


class LimitPageNumberPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
