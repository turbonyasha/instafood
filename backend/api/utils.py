from datetime import datetime

import api.constants as const


def get_shoplist_text(in_cart_recipes, ingredients_details):
    """Функция для формирования текстового списка покупок."""
    return '\n'.join([
        const.FILE_HEADER.format(
            date=datetime.now().strftime('%Y-%m-%d')
        ),
        const.INGREDIENTS,
        *[
            const.FILE_ROW.format(
                index=index,
                name=ingredient['ingredient'].capitalize(),
                amount=ingredient['amount'],
                measurement_unit=ingredient['measurement_unit']
            )
            for index, ingredient in enumerate(ingredients_details.values(), 1)
        ],
        const.FOR_RECIPES,
        *[recipe['name'] for recipe in in_cart_recipes]
    ])
