from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static

from recipes.views import (
    RecipeViewSet, TagsViewSet,
    redirect_to_recipe, IngredientsViewSet
)
from users.views import CustomUserViewSet, get_user_token, SubscriptionViewSet

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/subscriptions/', SubscriptionViewSet.as_view(
        {'get': 'list'}
    ), name='subscriptions-list'),
    path('api/', include(router.urls)),
    path('api/auth/token/login/', get_user_token, name='token-login'),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('<str:short_link>/', redirect_to_recipe, name='recipe_detail'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)