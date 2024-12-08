from django.http import HttpResponsePermanentRedirect

from recipes.models import Recipe
from .constants import REDIRECT_RECIPE


def redirect_to_recipe(request, recipe_id):
    """Реализует перенаправление с короткой ссылки."""
    if Recipe.objects.filter(id=recipe_id).exists():
        return HttpResponsePermanentRedirect(
            REDIRECT_RECIPE.format(
                recipe_id=recipe_id
            )
        )
