from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from catalog.models import Category, SimilarCategory
from catalog.serializers import (
    CategorySerializer,
    CategoryTreeSerializer,
    SimilarCategorySerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().prefetch_related("children")
    serializer_class = CategorySerializer

    def get_serializer_class(self):
        if self.action == "tree":
            return CategoryTreeSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["get"])
    def tree(self, request):
        roots = Category.objects.filter(parent__isnull=True)
        serializer = CategoryTreeSerializer(roots, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def subtree(self, request, pk=None):
        category = self.get_object()
        data = CategoryTreeSerializer(category).data
        return Response(data)


class SimilarCategoryViewSet(viewsets.ModelViewSet):
    queryset = SimilarCategory.objects.all()
    serializer_class = SimilarCategorySerializer
