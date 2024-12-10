from django.http import Http404
from django.shortcuts import redirect

from recipes.models import Recipe
from .constants import RECIPE_NOT_FOUND


def redirect_to_recipe(request, recipe_id):
    """Реализует перенаправление с короткой ссылки."""
    if Recipe.objects.filter(id=recipe_id).exists():
        return redirect(f'/recipes/{recipe_id}/')
    raise Http404(RECIPE_NOT_FOUND.format(
        id=recipe_id
    ))
