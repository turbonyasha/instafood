import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers


def random_filename(instance, filename):
    ext = filename.split('.')[-1]
    return f"{uuid.uuid4()}.{ext}"


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для преобразования base64 в изображение."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

    def create(self, validated_data):
        image = validated_data.get('image')
        if image:
            image.name = random_filename(self, image.name)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        image = validated_data.get('image')
        if image:
            image.name = random_filename(self, image.name)
        return super().update(instance, validated_data)
