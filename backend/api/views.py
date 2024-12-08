from django.db.models import Count, Exists, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from djoser.views import UserViewSet

import api.constants as const
from api.filters import RecipesFilterSet, UserFilterSet
from api.paginations import LimitPageNumberPagination
from api.permissions import SafeMethodPermission
from api.serializers import (
    IngredientSerializer, RecipeWriteSerializer, RecipeRetriveSerializer,
    TagSerializer, RecipesSubscriptionSerializer, FoodgramUserSerializer,
    SubscriptionSerializer
)
from api.utils import get_shoplist_text

from recipes.models import (
    FavoriteRecipes, Ingredient, Recipe,
    ShoppingCart, Tag, FoodgramUser, Subscription
)


class FoodgramUserViewSet(UserViewSet):
    """Представление для пользователя."""
    queryset = FoodgramUser.objects.all()
    serializer_class = FoodgramUserSerializer
    pagination_class = LimitPageNumberPagination
    filterset_class = UserFilterSet
    permission_classes = [SafeMethodPermission]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_anonymous:
            return queryset
        subscribe = self.request.user.subscribers.filter(
            author=OuterRef('pk')
        )
        queryset = queryset.annotate(
            is_subscribed_annotated=Exists(subscribe),
            recipes_count=Count('recipes')
        )
        return queryset

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        """Реализация обновления и удаления аватарки."""
        user = self.request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            raise ValidationError(serializer.errors)
        if user.avatar:
            user.avatar.delete()
        return Response(request.data, status=status.HTTP_204_NO_CONTENT)


class SubscriptionListView(APIView):
    """Представление для списка подписок"""
    permission_classes = [SafeMethodPermission]

    def get_queryset(self):
        return FoodgramUser.objects.filter(
            authors__user=self.request.user
        ).annotate(
            recipes_count=Count('recipes')
        )

    def get(self, request):
        return Response(SubscriptionSerializer(
            self.get_queryset(),
            many=True,
            context={'request': request}
        ).data)

    def perform_create(self, serializer):
        user = self.request.user
        author = serializer.validated_data['author']
        if user == author:
            raise ValidationError(const.SUBSCRIBTION_MYSELF)
        if Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError(const.SUBSCRIBTION_ALREADY)
        serializer.save(user=user)

    def post(self, request, id=None):
        author = get_object_or_404(FoodgramUser, id=id)
        Subscription.objects.create(user=request.user, author=author)
        return Response(SubscriptionSerializer(
            self.get_queryset().get(id=author.id),
            context={'request': request}
        ).data, status=status.HTTP_201_CREATED)

    def delete(self, request, id=None):
        get_object_or_404(
            Subscription,
            user=request.user,
            author=get_object_or_404(FoodgramUser, id=id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для рецептов."""
    queryset = Recipe.objects.all()
    http_method_names = const.HTTP_METHOD_NAMES
    permission_classes = [SafeMethodPermission]
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

    def _favorite_or_shopping_cart_action(
            self, request, model, user, recipe_pk
    ):
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        request_method = request.method
        if request_method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError(const.RECIPE_ALREADY.format(
                    message_text=(
                        const.FAVORITE if
                        model == FavoriteRecipes else const.SHOPCART
                    )
                ))
            model.objects.get_or_create(user=user, recipe=recipe)
            return Response(RecipesSubscriptionSerializer(
                recipe
            ).data, status=status.HTTP_201_CREATED)
        get_object_or_404(model, user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeRetriveSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk):
        """Возвращает короткую ссылку."""
        get_object_or_404(Recipe, pk=pk)
        return Response(
            {'short-link': request.build_absolute_uri(
                reverse(
                    'recipes:redirect_to_recipe',
                    args=[pk]
                )
            )}
        )

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        """Реализует работу Избранного."""
        return self._favorite_or_shopping_cart_action(
            request=request,
            model=FavoriteRecipes,
            user=request.user,
            recipe_pk=pk,
        )

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        """Реализует работу Корзины."""
        return self._favorite_or_shopping_cart_action(
            request=request,
            model=ShoppingCart,
            user=request.user,
            recipe_pk=pk,
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def get_and_download_shopping_cart(self, request):
        """Реализует получение пользователем файла со списком покупок."""
        ingredients_details = {}
        for recipe_ingredient in (
            self.request.user.shoppingcarts
            .prefetch_related('recipe__ingredients')
            .values('recipe__ingredients__name')
            .annotate(total_amount=Sum('recipe__recipe_ingredients__amount'))
            .values(
                'recipe__ingredients__name',
                'total_amount',
                'recipe__ingredients__measurement_unit'
            )
        ):
            ingredient_name = recipe_ingredient['recipe__ingredients__name']
            ingredients_details[ingredient_name] = {
                'ingredient': ingredient_name,
                'amount': recipe_ingredient['total_amount'],
                'measurement_unit': recipe_ingredient[
                    'recipe__ingredients__measurement_unit'
                ]
            }
        return FileResponse(
            get_shoplist_text(
                self.request.user.shoppingcarts.select_related(
                    'recipe'
                ).prefetch_related('recipe__ingredients'),
                ingredients_details
            ),
            as_attachment=True,
            filename=const.FILE_NAME.format(
                unique_name=timezone.now().strftime('%Y-%m-%d_%H-%M-%S')
            ),
            content_type='text/plain'
        )


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [SafeMethodPermission]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для игредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [SafeMethodPermission]
