import pytest
from catalog.models import Category, SimilarCategory
from catalog.serializers import (
    CategorySerializer,
    CategoryTreeSerializer,
    SimilarCategorySerializer,
)
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


@pytest.mark.django_db
def test_category_serializer_create():
    data = {
        "name": "Books",
        "description": "All books",
        "image": "https://example.com/image.jpg",
        "parent": None,
    }
    serializer = CategorySerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    category = serializer.save()
    assert category.name == "Books"
    assert category.parent is None


@pytest.mark.django_db
def test_category_tree_serializer():
    root = Category.objects.create(name="Root")
    child = Category.objects.create(name="Child", parent=root)
    grandchild = Category.objects.create(name="Grandchild", parent=child)

    serializer = CategoryTreeSerializer(root)
    data = serializer.data
    assert data["name"] == "Root"
    assert len(data["children"]) == 1
    assert data["children"][0]["name"] == "Child"
    assert data["children"][0]["children"][0]["name"] == "Grandchild"


@pytest.mark.django_db
def test_similar_category_serializer_valid():
    a = Category.objects.create(name="A")
    b = Category.objects.create(name="B")

    serializer = SimilarCategorySerializer(data={
        "category_a": a.id,
        "category_b": b.id
    })
    assert serializer.is_valid(), serializer.errors
    link = serializer.save()
    assert link.category_a.id < link.category_b.id


@pytest.mark.django_db
def test_similar_category_serializer_self_link():
    a = Category.objects.create(name="A")
    serializer = SimilarCategorySerializer(data={
        "category_a": a.id,
        "category_b": a.id
    })
    with pytest.raises(DRFValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_similar_category_serializer_duplicate_link():
    a = Category.objects.create(name="A")
    b = Category.objects.create(name="B")
    SimilarCategory.objects.create(category_a=a, category_b=b)
