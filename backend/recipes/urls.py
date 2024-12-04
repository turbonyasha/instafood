from django.urls import path
from recipes.views import redirect_to_recipe

urlpatterns = [
    path('s/<str:short_link>/', redirect_to_recipe, name='redirect_to_recipe'),
]
