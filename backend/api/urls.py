from django.urls import path, include
from rest_framework import routers

from api.views import (
    IngredientsViewSet, RecipeViewSet, TagsViewSet,
    FoodgramUserViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'users', FoodgramUserViewSet, basename='user')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
