# catalog/serializers.py
from rest_framework import serializers
from catalog.models import Category, SimilarCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "parent"]

class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "children"]

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.children.all(), many=True).data

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
