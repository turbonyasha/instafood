# from rest_framework import viewsets
# from rest_framework.pagination import PageNumberPagination

# from .models import Recipe, Tag
# from .serializers import TagSerializer, RecipeSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#     # pagination_class = PageNumberPagination
    
#     def perform_create(self, serializer):
#         # Вызываем метод create с дополнительным контекстом
#         serializer.save(author=self.request.user)