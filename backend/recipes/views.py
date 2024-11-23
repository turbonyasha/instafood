from rest_framework import viewsets
from rest_framework.decorators import action
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Recipe, Tag, Ingredient, FavoriteRecipes
from .serializers import TagSerializer, RecipeCUDSerializer, RecipeRetriveSerializer, IngredientSerializer
from users.serializers import RecipesSubscriptionSerializer
from .utils import generate_short_link


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'delete', 'patch')
    
    def perform_create(self, serializer):
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
    
    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        user = self.request.user
        try:
            recipe = Recipe.objects.get(pk=pk)
            # author = recipe.author
        except Recipe.DoesNotExist:
            return Response({'detail': 'Рецепт не найден.'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            # if user == author:
            #     return Response({'detail': 'Вы не можете подписаться на самого себя.'}, status=status.HTTP_400_BAD_REQUEST)
            if FavoriteRecipes.objects.filter(user=user, recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже в вашем избранном.'}, status=status.HTTP_400_BAD_REQUEST)
            favorites = FavoriteRecipes(user=user, recipe=recipe)
            favorites.save()
            serializer = RecipesSubscriptionSerializer(recipe, context={'request': request, 'user': user})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                favorites = FavoriteRecipes.objects.get(user=user, recipe=recipe)
                favorites.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except FavoriteRecipes.DoesNotExist:
                return Response({'detail': 'Рецепт не в вашем избранном.'}, status=status.HTTP_404_NOT_FOUND)


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