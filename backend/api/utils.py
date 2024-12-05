from datetime import datetime

import api.constants as const


def get_shoplist_text(in_cart_recipes, ingredients, ingredients_summary):
    """Функция для формирования текстового списка покупок."""
    ingredients_list = [
        const.FILE_ROW.format(
            index=index,
            name=str(ingredient_name).capitalize(),
            amount=amount,
            measurement_unit=ingredient.measurement_unit
        )
        for index, (ingredient_name, amount) in enumerate(
            ingredients_summary.items(), 1
        )
        if (ingredient := ingredients.get(ingredient_name))
    ]
    recipes_list = [cart_item.recipe.name for cart_item in in_cart_recipes]
    return '\n'.join([
        const.FILE_HEADER.format(
            date=datetime.now().strftime('%Y-%m-%d')
        ),
        const.INGREDIENTS,
        *ingredients_list,
        const.FOR_RECIPES,
        *recipes_list
    ])
