from django.http import Http404
from django.shortcuts import redirect

from recipes.models import Recipe


def redirect_to_recipe(request, recipe_id):
    """Реализует перенаправление с короткой ссылки."""
    if Recipe.objects.filter(id=recipe_id).exists():
        return redirect(f'/recipes/{recipe_id}/')
    raise Http404('Рецепт не найден.')
