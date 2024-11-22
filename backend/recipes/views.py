from rest_framework import viewsets
from rest_framework.decorators import action
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Recipe, Tag, Ingredient
from .serializers import TagSerializer, RecipeCUDSerializer, RecipeRetriveSerializer, IngredientSerializer
from .utils import generate_short_link


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'delete', 'patch')
    
    def perform_create(self, serializer):
        # Вызываем метод create с дополнительным контекстом
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeRetriveSerializer
        return RecipeCUDSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk):
        recipe = self.get_object()
        if recipe.short_link:
            short_link = recipe.short_link
        else:
            short_link = generate_short_link()
            recipe.short_link = short_link
            recipe.save()
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


def redirect_to_recipe(request, short_link):
    return redirect('recipe-detail', pk=get_object_or_404(Recipe, short_link=short_link).pk)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None