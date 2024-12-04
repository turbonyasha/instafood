from collections import defaultdict
from datetime import datetime

import api.constants as const


def get_shoplist_text(in_cart_recipes):
    """Функция для формирования текстового списка покупок."""
    recipes_names = [cart_item.recipe.name for cart_item in in_cart_recipes]
    file_header_recipes = ', '.join(recipes_names)
    ingredients_list = [
        const.FILE_ROW.format(
            index=index,
            name=ingredient_name.capitalize(),
            amount=amount,
            measurement_unit=ingredients.get(ingredient_name).measurement_unit
        )
        for index, (ingredient_name, amount) in enumerate(ingredients_summary.items(), 1)
        if (ingredient := ingredients.get(ingredient_name))
    ]
    recipes_list = [recipe.name for recipe in in_cart_recipes]
    return '\n'.join([
        const.FILE_HEADER.format(file_header=file_header_recipes, date=datetime.now().strftime('%Y-%m-%d')),
        'Шапка продуктов',
        *ingredients_list,
        'Шапка рецептов',
        *recipes_list
    ])
