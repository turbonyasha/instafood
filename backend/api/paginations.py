from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Кастомная пагинация с измененным наименованием параметра."""
    page_size = 6
    page_size_query_param = 'limit'
