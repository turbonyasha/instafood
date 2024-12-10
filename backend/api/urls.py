from django.urls import path, include
from rest_framework import routers

from api.views import (
    FoodgramUserViewSet, IngredientsViewSet,
    RecipeViewSet, SubscriptionListView, TagsViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'users', FoodgramUserViewSet, basename='user')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionListView.as_view(),
        name='subscriptions-list'
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
