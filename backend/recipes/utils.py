from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import random
from django.conf import settings

SHORT_LINK_LENGHT = 10
SHORT_LINK_STR = 'qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM'



class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')
            # И извлечь расширение файла.
            ext = format.split('/')[-1]  
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def generate_short_link():
    short_url = ''
    for _ in range(SHORT_LINK_LENGHT):
        short_url += random.choice(SHORT_LINK_STR)
    return settings.PROJECT_URL + short_url