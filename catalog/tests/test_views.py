import pytest
from rest_framework.test import APIClient

from catalog.models import Category, SimilarCategory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def setup_categories():
    root = Category.objects.create(name="Electronics")
    laptops = Category.objects.create(name="Laptops", parent=root)
    phones = Category.objects.create(name="Phones", parent=root)
    Category.objects.create(name="Gaming Laptops", parent=laptops)
    Category.objects.create(name="Smartphones", parent=phones)
    return root


def test_category_list(client, setup_categories):
    response = client.get("/api/categories/")
    assert response.status_code == 200
    assert any(cat["name"] == "Electronics" for cat in response.json()["results"])


def test_category_tree(client, setup_categories):
    response = client.get("/api/categories/tree/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["name"] == "Electronics"
    assert "children" in response.json()[0]


def test_category_subtree(client, setup_categories):
    laptops = Category.objects.get(name="Laptops")
    response = client.get(f"/api/categories/{laptops.id}/subtree/")
    assert response.status_code == 200
    assert response.json()["name"] == "Laptops"
    assert any(child["name"] == "Gaming Laptops" for child in response.json()["children"])


def test_similarity_api(client, setup_categories):
    a = Category.objects.get(name="Laptops")
    b = Category.objects.get(name="Phones")
    SimilarCategory.objects.create(category_a=a, category_b=b)

    response = client.get("/api/similarities/")
    assert response.status_code == 200
    results = response.json()["results"]
    assert any(
        (entry["category_a"] == a.id and entry["category_b"] == b.id) or
        (entry["category_a"] == b.id and entry["category_b"] == a.id)
        for entry in results
    )
