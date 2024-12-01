from collections import defaultdict
from urllib.parse import urljoin

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from . import constants as const
from api.filters import RecipesFilterSet, UserFilterSet
from api.permissions import AdminOrSafeMethodPermission
from api.utils import favorite_or_shopping_cart_action

from .models import (
    FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag
)
from api.serializers import (
    IngredientSerializer, RecipeCUDSerializer,
    RecipeRetriveSerializer, TagSerializer
)
from django.db.models import Count, Exists, OuterRef
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from api.paginations import LimitPageNumberPagination

from .models import FoodgramUser, Subscription
from api.serializers import (
    CustomTokenCreateSerializer, CustomUserSerializer,
    SubscribtionSerializer
)
from api.serializers import RecipesSubscriptionSerializer


class CustomUserViewSet(UserViewSet):
    """Представление для пользователя."""
    queryset = FoodgramUser.objects.all().order_by('id')
    serializer_class = CustomUserSerializer
    pagination_class = LimitPageNumberPagination
    filterset_class = UserFilterSet

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [AllowAny()]
        if self.action in ['avatar', 'subscribe', 'subscriptions']:
            return [IsAuthenticated()]
        return [AdminOrSafeMethodPermission()]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_anonymous:
            return queryset
        subscribe = self.request.user.subscriptions.filter(
            author=OuterRef('pk')
        )
        queryset = queryset.annotate(
            is_subscribed_annotated=Exists(subscribe),
            recipes_count=Count('recipe')
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
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            return Response(request.data, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        """Реализация добавления и удаления подписки на автора."""
        self.permission_classes = [IsAuthenticated]
        user = self.request.user
        try:
            author = FoodgramUser.objects.get(id=id)
        except FoodgramUser.DoesNotExist:
            return Response(
                {'detail': const.USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'detail': const.SUBSCRIBTION_MYSELF},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription, created = Subscription.objects.get_or_create(
                user=user, author=author
            )
            if not created:
                return Response(
                    {'detail': const.SUBSCRIBTION_ALREADY},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribtionSerializer(
                subscription, context={'request': request, 'user': user}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                subscription = Subscription.objects.get(
                    user=user, author=author
                )
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscription.DoesNotExist:
                return Response(
                    {'detail': const.SUBSCRIPTION_NOTFOUND},
                    status=status.HTTP_404_NOT_FOUND
                )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Представление для списка подписок"""
    serializer_class = SubscribtionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        author = serializer.validated_data['author']
        if user == author:
            raise serializers.ValidationError(const.SUBSCRIBTION_MYSELF)
        subscription, created = Subscription.objects.get_or_create(
            user=user, author=author
        )
        if not created:
            raise serializers.ValidationError(const.SUBSCRIBTION_ALREADY)
        return subscription

    def perform_destroy(self, instance):
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_user_token(request):
    """Получение токена пользователя по email и паролю."""
    serializer = CustomTokenCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = FoodgramUser.objects.get(
            email=serializer.validated_data['email']
        )
    except FoodgramUser.DoesNotExist:
        raise ValidationError(const.AUTH_FAIL_TEXT)
    if not user.check_password(serializer.validated_data['password']):
        raise ValidationError(const.AUTH_FAIL_TEXT)
    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {'auth_token': token.key},
        status=status.HTTP_200_OK
    )


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для рецептов."""
    queryset = Recipe.objects.all()
    http_method_names = const.HTTP_METHOD_NAMES
    permission_classes = [IsAuthenticatedOrReadOnly]
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
        request_method, model, user, recipe_pk, message_text
    ):
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        if request_method == 'POST':
            model.objects.get_or_create(user=user, recipe=recipe)
            serializer = RecipesSubscriptionSerializer(
                recipe, context={'user': user}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request_method == 'DELETE':
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeRetriveSerializer
        return RecipeCUDSerializer

    # def create(self, request, *args, **kwargs):
    #     self.permission_classes = [IsAuthorOrAdmin]
    #     return super().create(request, *args, **kwargs)

    # def update(self, request, *args, **kwargs):
    #     self.permission_classes = [IsAuthorOrAdmin]
    #     return super().update(request, *args, **kwargs)

    # def destroy(self, request, *args, **kwargs):
    #     self.permission_classes = [IsAuthorOrAdmin]
    #     return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk):
        """Возвращает короткую ссылку."""
        recipe = self.get_object()
        if recipe.short_link:
            short_link = recipe.short_link
        else:
            short_link = str(recipe.id)
        recipe.save()
        print(urljoin(const.PROJECT_URL + '/', short_link))
        return Response(
            {'short-link': urljoin(const.PROJECT_URL + '/', short_link)},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        """Реализует работу Избранного."""
        user = self.request.user
        tags = request.query_params.get('tags', None)
        queryset = Recipe.objects.filter(id=pk)
        if tags:
            queryset = queryset.filter(tags__name__icontains=tags)
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
        in_cart_recipes = ShoppingCart.objects.filter(
            user=self.request.user
        ).select_related('recipe')
        ingredients_summary = defaultdict(int)
        recipes_names = []
        for recipe in in_cart_recipes:
            recipes_names.append(recipe.recipe.name)
            recipes = RecipeIngredient.objects.filter(
                recipe=recipe.recipe
            )
            for recipe in recipes:
                ingredients_summary[recipe.ingredient.name] += (
                    recipe.amount
                )
        file_header = ', '.join(recipes_names)
        shopping_list = [const.FILE_HEADER.format(
            file_header=file_header
        )]
        for ingredient_name, amount in ingredients_summary.items():
            ingredient = Ingredient.objects.filter(
                name=ingredient_name).first()
            shopping_list.append(const.FILE_ROW.format(
                ingredient=ingredient_name,
                amount=amount,
                measurement_unit=ingredient.measurement_unit
            ))
        response = HttpResponse(
            '\n'.join(shopping_list),
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{const.FILENAME}.txt"'
        )
        return response


def redirect_to_recipe(request, short_link):
    """Реализует перенаправление с короткой ссылки."""
    recipe = get_object_or_404(
        Recipe, short_link=short_link
    )
    absolute_url = recipe.get_absolute_url()
    if absolute_url.startswith('/api/'):
        absolute_url = absolute_url.replace('/api/', '/')
    return HttpResponseRedirect(absolute_url)


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
