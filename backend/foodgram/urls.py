from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from api.views import (
    IngredientsViewSet, RecipeViewSet, TagsViewSet,
    FoodgramUserViewSet, SubscriptionViewSet
)
from recipes.views import redirect_to_recipe

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'users', FoodgramUserViewSet, basename='user')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/subscriptions/', SubscriptionViewSet.as_view(
        {'get': 'list'}
    ), name='subscriptions-list'),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('s/<str:short_link>/',
         redirect_to_recipe,
         name='redirect_to_recipe'
         ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
