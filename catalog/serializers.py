from django.db.models import Q
from rest_framework import serializers

from catalog.models import Category, SimilarCategory


class CategorySerializer(serializers.ModelSerializer):
    similar_to = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        read_only=True
    )

    children = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )

    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    def validate(self, data):
        instance = self.instance or Category(**data)
        for attr, value in data.items():
            setattr(instance, attr, value)

        instance.full_clean()
        return data

    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "children", "parent", "similar_to"]


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    similar_to = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

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

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


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

        return data
