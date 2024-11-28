from collections import defaultdict

from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Exists, OuterRef
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)

from .models import (
    Recipe, Tag, Ingredient, FavoriteRecipes,
    RecipeIngredient, ShoppingCart
)
from .serializers import (
    TagSerializer, RecipeCUDSerializer,
    RecipeRetriveSerializer, IngredientSerializer
)
import core.constants as const
from core.utils import generate_short_link, favorite_or_shopping_cart_action
from core.permissions import (
    IsAuthorOrAdmin, AdminOrSafeMethodPermission,
    AdminOrSafeMethodPermission
)
from core.filters import RecipesFilterSet


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для рецептов."""
    queryset = Recipe.objects.all()
    http_method_names = const.HTTP_METHOD_NAMES
    permission_classes = [AdminOrSafeMethodPermission]
    filterset_class = RecipesFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            for model_class, annotation_name in [
                (ShoppingCart, 'is_in_shopping_cart_annotated'),
                (FavoriteRecipes, 'is_favorited_annotated')
            ]:
                is_in_list_exists = Exists(
                    model_class.objects.filter(
                        recipe=OuterRef('pk'),
                        user=self.request.user
                    )
                )
                queryset = queryset.annotate(
                    **{annotation_name: is_in_list_exists}
                )
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
        """Возвращает короткую ссылку."""
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
        """Реализует работу Избранного."""
        user = self.request.user
        return favorite_or_shopping_cart_action(
            request_method=self.request.method,
            model=FavoriteRecipes,
            user=user,
            recipe_pk=pk,
            message_text=const.FAVORITE_VIEW
        )

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        """Реализует работу Корзины."""
        user = self.request.user
        return favorite_or_shopping_cart_action(
            request_method=self.request.method,
            model=ShoppingCart,
            user=user,
            recipe_pk=pk,
            message_text=const.SHOPPING_CART_VIEW
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def get_and_download_shopping_cart(self, request):
        """Реализует получение файла со списком покупок."""
        favorite_recipes = FavoriteRecipes.objects.filter(
            user=self.request.user
        ).select_related('recipe')
        ingredients_summary = defaultdict(int)
        recipes_names = []
        for favorite in favorite_recipes:
            recipes_names.append(favorite.recipe.name)
            ingredients = RecipeIngredient.objects.filter(
                recipe=favorite.recipe
            )
            for ingredient in ingredients:
                ingredients_summary[ingredient.ingredient] += ingredient.amount
        shopping_list = [const.FILE_HEADER.format(
            file_header=', '.join(recipes_names)
        )]
        for ingredient, amount in ingredients_summary.items():
            shopping_list.append(const.FILE_ROW.format(
                ingredient=ingredient.name,
                amount=amount,
                measurement_unit=ingredient.measurement_unit
            ))
        filename = const.FILENAME
        response = HttpResponse(
            '\n'.join(shopping_list),
            content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


def redirect_to_recipe(request, short_link):
    """Реализует перенаправление с короткой ссылки."""
    return redirect('recipe-detail', pk=get_object_or_404(
        Recipe, short_link=short_link
    ).pk)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AdminOrSafeMethodPermission]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для игредиентов."""
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
