from django.http import HttpResponsePermanentRedirect

from recipes.models import Recipe


def redirect_to_recipe(request, recipe_id):
    """Реализует перенаправление с короткой ссылки."""
    if Recipe.objects.filter(id=recipe_id).exists():
        return HttpResponsePermanentRedirect(f'/recipes/{recipe_id}/')
