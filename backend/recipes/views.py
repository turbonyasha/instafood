from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from recipes.models import Recipe


def redirect_to_recipe(request, short_link):
    """Реализует перенаправление с короткой ссылки."""
    recipe = get_object_or_404(
        Recipe, id=int(short_link)
    )
    return redirect(recipe.get_absolute_url())
