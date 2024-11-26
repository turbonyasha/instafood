from collections import defaultdict

from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Exists, OuterRef
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


from .models import (
    Recipe, Tag, Ingredient, FavoriteRecipes,
    RecipeIngredient, ShoppingCart
)
from .serializers import (
    TagSerializer, RecipeCUDSerializer,
    RecipeRetriveSerializer, IngredientSerializer
)
import core.constants as const
from core.utils import generate_short_link
from core.permissions import IsAuthorOrAdmin, AdminOrSafeMethodPermission
from core.filters import RecipesFilterSet
from users.serializers import RecipesSubscriptionSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = const.HTTP_METHOD_NAMES
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = RecipesFilterSet

    # def get_queryset(self):
    # queryset = super().get_queryset()
    # if self.request.user.is_authenticated:
    #     for model_class, annotation_name in [
    #         (ShoppingCart, 'is_in_shopping_cart'),
    #         (FavoriteRecipes, 'is_favorited')
    #     ]:
    #         is_in_list_exists = Exists(
    #             model_class.objects.filter(
    #                 recipe=OuterRef('pk'),
    #                 user=self.request.user
    #             )
    #         )
    #         queryset = queryset.annotate(**{annotation_name: is_in_list_exists})
    # return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            shopping_cart_exists = Exists(
                ShoppingCart.objects.filter(
                    recipe=OuterRef('pk'),
                    user=self.request.user
                )
            )
            queryset = queryset.annotate(is_in_shopping_cart_annotated=shopping_cart_exists)
        if self.request.user.is_authenticated:
            favorites_exists = Exists(
                FavoriteRecipes.objects.filter(
                    recipe=OuterRef('pk'),
                    user=self.request.user
                )
            )
            queryset = queryset.annotate(is_favorited_annotated=favorites_exists)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeRetriveSerializer
        return RecipeCUDSerializer

    def create(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthorOrAdmin]
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthorOrAdmin]
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthorOrAdmin]
        return super().destroy(request, *args, **kwargs)

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
        except Recipe.DoesNotExist:
            return Response({'detail': 'Рецепт не найден.'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
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
    
    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Рецепт не найден.'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже в вашей корзине.'}, status=status.HTTP_400_BAD_REQUEST)
            shopping_cart_recipe = ShoppingCart(user=user, recipe=recipe)
            shopping_cart_recipe.save()
            serializer = RecipesSubscriptionSerializer(recipe, context={'request': request, 'user': user})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                favorites = FavoriteRecipes.objects.get(user=user, recipe=recipe)
                favorites.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except FavoriteRecipes.DoesNotExist:
                return Response({'detail': 'Рецепт не в вашей корзине.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart', permission_classes=[IsAuthenticated])
    def get_and_download_shopping_cart(self, request):
        favorite_recipes = FavoriteRecipes.objects.filter(user=self.request.user).select_related('recipe')
        ingredients_summary = defaultdict(int)
        recipes_names = []
        for favorite in favorite_recipes:
            recipes_names.append(favorite.recipe.name)
            ingredients = RecipeIngredient.objects.filter(recipe=favorite.recipe)
            for ingredient in ingredients:
                ingredients_summary[ingredient.ingredient] += ingredient.amount
        file_header = ", ".join(recipes_names)
        shopping_list = [f'Список покупок для рецептов: {file_header}']
        for ingredient, amount in ingredients_summary.items():
            shopping_list.append(f"▢ {ingredient.name}: {amount} {ingredient.measurement_unit}")
        content = "\n".join(shopping_list)
        filename = "shopping_cart.txt"
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


def redirect_to_recipe(request, short_link):
    return redirect('recipe-detail', pk=get_object_or_404(
        Recipe, short_link=short_link
    ).pk)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AdminOrSafeMethodPermission]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [AdminOrSafeMethodPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_param = self.request.query_params.get('name', None)
        if search_param:
            queryset = queryset.filter(name__icontains=search_param)
        return queryset
