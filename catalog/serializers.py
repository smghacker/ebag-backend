# catalog/serializers.py
from django.db.models import Q
from rest_framework import serializers

from catalog.models import Category, SimilarCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "parent"]


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    similar_to = serializers.SerializerMethodField()  # 👈 NEW

    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "children", "similar_to"]

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.children.all(), many=True).data

    def get_similar_to(self, obj):
        links = SimilarCategory.objects.filter(
            Q(category_a=obj) | Q(category_b=obj)
        )
        related_ids = {
            link.category_b.id if link.category_a == obj else link.category_a.id
            for link in links
        }
        names = Category.objects.filter(id__in=related_ids).values_list("name", flat=True)
        return sorted(names)


class SimilarCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SimilarCategory
        fields = ["id", "category_a", "category_b"]

    def validate(self, data):
        if data["category_a"] == data["category_b"]:
            raise serializers.ValidationError("A category cannot be similar to itself.")

        # Normalize ordering for symmetry
        a_id = data["category_a"].id
        b_id = data["category_b"].id

        if a_id > b_id:
            data["category_a"], data["category_b"] = data["category_b"], data["category_a"]

        # Check if the pair already exists
        if SimilarCategory.objects.filter(
                category_a=data["category_a"],
                category_b=data["category_b"],
        ).exists():
            raise serializers.ValidationError("This similarity already exists.")

        return data
