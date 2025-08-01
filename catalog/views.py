from django.db.models import Q
from rest_framework import status
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

    def get_queryset(self):
        queryset = super().get_queryset()
        parent_id = self.request.query_params.get("parent")
        if parent_id is not None:
            queryset = queryset.filter(parent_id=parent_id)
        return queryset

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

    @action(detail=False, methods=["get"])
    def by_depth(self, request):
        try:
            target_depth = int(request.query_params.get("depth", -1))
        except ValueError:
            return Response({"detail": "Invalid depth"}, status=400)

        if target_depth < 0:
            return Response({"detail": "Depth must be non-negative"}, status=400)

        # Efficient filtering using Python in-memory property (for small category counts)
        matching = [c for c in Category.objects.all() if c.depth == target_depth]
        serializer = self.get_serializer(matching, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="move-up")
    def move_up(self, request, pk=None):
        return self._move(pk, request, direction="up")

    @action(detail=True, methods=["post"], url_path="move-down")
    def move_down(self, request, pk=None):
        return self._move(pk, request, direction="down")

    def _move(self, pk, request, direction):
        try:
            steps = int(request.query_params.get("steps", 1))
            if steps < 0:
                raise ValueError()
        except ValueError:
            return Response({"detail": "steps must be a positive integer"}, status=400)
        category = self.get_object()
        siblings = list(category.parent.children.order_by("order") if category.parent else Category.objects.filter(
            parent=None).order_by("order"))
        idx = siblings.index(category)

        if direction == "up":
            new_idx = max(0, idx - steps)
        elif direction == "down":
            new_idx = min(len(siblings) - 1, idx + steps)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if new_idx != idx:
            siblings.insert(new_idx, siblings.pop(idx))
            for i, cat in enumerate(siblings):
                if cat.order != i:
                    cat.order = i
                    cat.save(update_fields=["order"])

        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if Category.objects.filter(parent=instance).exists():
            return Response(
                {"detail": "Cannot delete a category with children."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.full_clean()
        instance.save()


class SimilarCategoryViewSet(viewsets.ModelViewSet):
    queryset = SimilarCategory.objects.all()
    serializer_class = SimilarCategorySerializer

    def create(self, request, *args, **kwargs):
        category_a = request.data.get("category_a")
        category_b = request.data.get("category_b")

        if category_a == category_b:
            return Response({"detail": "A category cannot be similar to itself."},
                            status=status.HTTP_400_BAD_REQUEST)

        exists = SimilarCategory.objects.filter(
            Q(category_a=category_a, category_b=category_b) |
            Q(category_a=category_b, category_b=category_a)
        ).exists()

        if exists:
            return Response(status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Editing similarities is not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "Editing similarities is not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
