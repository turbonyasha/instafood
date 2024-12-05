from django.shortcuts import redirect
from django.urls import reverse

from recipes.models import Recipe


def redirect_to_recipe(request, recipe_id):
    """Реализует перенаправление с короткой ссылки."""
    if Recipe.objects.filter(id=int(recipe_id)).exists():
        return redirect(reverse('api:recipes-detail', args=[recipe_id]))
