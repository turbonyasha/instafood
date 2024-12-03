from collections import defaultdict
from urllib.parse import urljoin

from io import BytesIO
from django.http import FileResponse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.urls import reverse

from . import constants as const
from api.filters import RecipesFilterSet, UserFilterSet
from api.permissions import AdminOrSafeMethodPermission
from api.utils import favorite_or_shopping_cart_action

from recipes.models import (
    FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag
)
from api.serializers import (
    IngredientSerializer, RecipeWriteSerializer,
    RecipeRetriveSerializer, TagSerializer
)
from django.db.models import Count, Exists, OuterRef
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from api.paginations import LimitPageNumberPagination

from recipes.models import FoodgramUser, Subscription
from api.serializers import (
    FoodgramUserSerializer,
    SubscribtionSerializer
)
from api.serializers import RecipesSubscriptionSerializer
from api.utils import get_shoplist_text


class FoodgramUserViewSet(UserViewSet):
    """Представление для пользователя."""
    queryset = FoodgramUser.objects.all()
    serializer_class = FoodgramUserSerializer
    pagination_class = LimitPageNumberPagination
    filterset_class = UserFilterSet

    # def get_permissions(self):
    #     if self.action in ['list', 'retrieve', 'create']:
    #         return [AllowAny()]
    #     if self.action in ['avatar', 'subscribe', 'subscriptions']:
    #         return [IsAuthenticated()]
    #     return [AdminOrSafeMethodPermission()]

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
            raise ValidationError(serializer.errors)
        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            return Response(request.data, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        """Реализация добавления и удаления подписки на автора."""
        self.permission_classes = [IsAuthenticated]
        user = self.request.user
        author = get_object_or_404(FoodgramUser, id=id)
        if request.method == 'POST':
            if user == author:
                raise ValidationError({'detail': const.SUBSCRIBTION_MYSELF})
            subscription, created = Subscription.objects.get_or_create(
                user=user, author=author
            )
            if not created:
                raise ValidationError({'detail': const.SUBSCRIBTION_ALREADY})
            return Response(SubscribtionSerializer(
                subscription, context={'request': request, 'user': user}
            ).data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            Subscription, user=user, author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Представление для списка подписок"""
    serializer_class = SubscribtionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.subscribers.all()

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


# @api_view(['POST'])
# @permission_classes([permissions.AllowAny])
# def get_user_token(request):
#     """Получение токена пользователя по email и паролю."""
#     serializer = CustomTokenCreateSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     try:
#         user = FoodgramUser.objects.get(
#             email=serializer.validated_data['email']
#         )
#     except FoodgramUser.DoesNotExist:
#         raise ValidationError(const.AUTH_FAIL_TEXT)
#     if not user.check_password(serializer.validated_data['password']):
#         raise ValidationError(const.AUTH_FAIL_TEXT)
#     token, created = Token.objects.get_or_create(user=user)

#     return Response(
#         {'auth_token': token.key},
#         status=status.HTTP_200_OK
#     )


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
        return RecipeWriteSerializer

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
        short_link = str(self.get_object().id)
        short_link_url = reverse('redirect_to_recipe', args=[short_link])
        full_url = request.build_absolute_uri(short_link_url)
        return Response(
            {'short-link': full_url}
        )

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        """Реализует работу Избранного."""
        user = self.request.user
        # tags = request.query_params.get('tags', None)
        # queryset = Recipe.objects.filter(id=pk)
        # if tags:
        #     queryset = queryset.filter(tags__name__icontains=tags)
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
        """Реализует получение пользователем файла со списком покупок."""
        in_cart_recipes = ShoppingCart.objects.filter(
            user=self.request.user
        ).select_related('recipe').prefetch_related('recipe__ingredients')
        buffer = BytesIO()
        buffer.write(get_shoplist_text(in_cart_recipes).encode('utf-8'))
        buffer.seek(0)
        return FileResponse(
            buffer,
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
    permission_classes = [AdminOrSafeMethodPermission]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для игредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [AdminOrSafeMethodPermission]
