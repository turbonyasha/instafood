from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Recipe, Tag
from .serializers import TagSerializer, RecipeCUDSerializer, RecipeRetriveSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # pagination_class = PageNumberPagination
    
    def perform_create(self, serializer):
        # Вызываем метод create с дополнительным контекстом
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeRetriveSerializer
        return RecipeCUDSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
