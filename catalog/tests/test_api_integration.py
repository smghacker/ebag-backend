from pathlib import Path

import pytest
from rest_framework.test import APIClient

from catalog.models import Category


@pytest.mark.django_db
class TestCategoryAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_list_categories(self):
        Category.objects.create(name="A", description="A")
        Category.objects.create(name="B", description="B")
        response = self.client.get("/api/categories/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 2

    def test_category_tree(self):
        root = Category.objects.create(name="Parent", description="Root")
        Category.objects.create(name="Child", description="Child", parent=root)
        response = self.client.get("/api/categories/tree/")
        assert response.status_code == 200
        assert any("children" in cat for cat in response.json())

    def test_category_subtree(self):
        root = Category.objects.create(name="Root", description="Tree Root")
        Category.objects.create(name="Child", description="Child", parent=root)
        response = self.client.get(f"/api/categories/{root.id}/subtree/")
        assert response.status_code == 200
        assert response.json()["id"] == root.id

    def test_create_and_patch_category(self):
        root = Category.objects.create(name="Parent", description="Root")
        img_path = Path(__file__).parent / "test-images" / "fruits.jpeg"
        with open(img_path, "rb") as img:
            response = self.client.post("/api/categories/", {
                "name": "TestCategory",
                "description": "Test Desc",
                "parent": root.id,
                "children": [],
                "image": img
            }, format="multipart")
        assert response.status_code == 201
        cat_id = response.json()["id"]

        response = self.client.patch(f"/api/categories/{cat_id}/", {"name": "Updated"}, format="json")
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    def test_delete_category(self):
        cat = Category.objects.create(name="ToDelete", description="X")
        response = self.client.delete(f"/api/categories/{cat.id}/")
        assert response.status_code == 204

    def test_similarities_crud(self):
        c1 = Category.objects.create(name="A", description="X")
        c2 = Category.objects.create(name="B", description="Y")
        response = self.client.post("/api/similarities/", {
            "category_a": c1.id,
            "category_b": c2.id
        }, format="json")
        assert response.status_code == 201
        sim_id = response.json()["id"]

        get_resp = self.client.get(f"/api/similarities/{sim_id}/")
        assert get_resp.status_code == 200

        patch_resp = self.client.patch(f"/api/similarities/{sim_id}/", {
            "category_b": c1.id
        }, format="json")
        assert patch_resp.status_code == 405

        del_resp = self.client.delete(f"/api/similarities/{sim_id}/")
        assert del_resp.status_code == 204

    def test_get_categories_by_depth(self):
        client = APIClient()

        # Create a tree like:
        # Root
        # ├── Child1
        # │   └── Grandchild1
        # └── Child2

        root = Category.objects.create(name="Root")
        child1 = Category.objects.create(name="Child1", parent=root)
        child2 = Category.objects.create(name="Child2", parent=root)
        grandchild1 = Category.objects.create(name="Grandchild1", parent=child1)

        # Check depth=0 (root)
        response = client.get("/api/categories/by_depth/?depth=0")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Root"

        # Check depth=1 (children)
        response = client.get("/api/categories/by_depth/?depth=1")
        assert response.status_code == 200
        names = {cat["name"] for cat in response.data}
        assert names == {"Child1", "Child2"}

        # Check depth=2 (grandchild)
        response = client.get("/api/categories/by_depth/?depth=2")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Grandchild1"

        # Check invalid input
        response = client.get("/api/categories/by_depth/?depth=abc")
        assert response.status_code == 400
        assert "Invalid depth" in response.data["detail"]


@pytest.mark.django_db
class TestCategoryReordering:
    def setup_method(self):
        self.client = APIClient()

        # Create parent and children categories with order
        self.parent = Category.objects.create(name="Parent")
        self.cat_a = Category.objects.create(name="A", parent=self.parent, order=0)
        self.cat_b = Category.objects.create(name="B", parent=self.parent, order=1)
        self.cat_c = Category.objects.create(name="C", parent=self.parent, order=2)

    def get_ordered_names(self):
        return list(self.parent.children.order_by("order").values_list("name", flat=True))

    def test_move_category_up(self):
        url = f"/api/categories/{self.cat_c.id}/move-up/?steps=2"
        resp = self.client.post(url)
        assert resp.status_code == 200
        assert self.get_ordered_names() == ["C", "A", "B"]

    def test_move_category_down(self):
        url = f"/api/categories/{self.cat_a.id}/move-down/?steps=2"
        resp = self.client.post(url)
        assert resp.status_code == 200
        assert self.get_ordered_names() == ["B", "C", "A"]

    def test_move_category_up_boundary(self):
        url = f"/api/categories/{self.cat_a.id}/move-up/?steps=10"
        resp = self.client.post(url)
        assert resp.status_code == 200
        assert self.get_ordered_names() == ["A", "B", "C"]

    def test_move_category_down_boundary(self):
        url = f"/api/categories/{self.cat_c.id}/move-down/?steps=5"
        resp = self.client.post(url)
        assert resp.status_code == 200
        assert self.get_ordered_names() == ["A", "B", "C"]


@pytest.mark.django_db
class TestCategoryConstraints:
    def setup_method(self):
        self.client = APIClient()

    def test_self_parent_not_allowed(self):
        cat = Category.objects.create(name="SelfRef", description="Invalid")
        response = self.client.patch(f"/api/categories/{cat.id}/", {"parent": cat.id}, format="json")
        assert response.status_code == 400

    def test_loop_not_allowed(self):
        a = Category.objects.create(name="A", description="A")
        b = Category.objects.create(name="B", description="B", parent=a)
        c = Category.objects.create(name="C", description="C", parent=b)
        response = self.client.patch(f"/api/categories/{a.id}/", {"parent": c.id}, format="json")
        assert response.status_code in (400, 409)

    def test_move_category(self):
        p1 = Category.objects.create(name="P1", description="Old")
        p2 = Category.objects.create(name="P2", description="New")
        child = Category.objects.create(name="X", description="Child", parent=p1)
        response = self.client.patch(f"/api/categories/{child.id}/", {"parent": p2.id}, format="json")
        assert response.status_code == 200
        assert response.json()["parent"] == p2.id

    def test_cannot_delete_category_with_children(self):
        parent = Category.objects.create(name="Parent", description="Has kids")
        Category.objects.create(name="Child", description="Kid", parent=parent)
        response = self.client.delete(f"/api/categories/{parent.id}/")
        assert response.status_code in (400, 409)


@pytest.mark.django_db
class TestRetrievalOptions:
    def setup_method(self):
        self.client = APIClient()

    def test_by_id(self):
        cat = Category.objects.create(name="FindMe", description="Test")
        response = self.client.get(f"/api/categories/{cat.id}/")
        assert response.status_code == 200
        assert response.json()["id"] == cat.id

    def test_by_parent(self):
        parent = Category.objects.create(name="P", description="X")
        child = Category.objects.create(name="C", description="Y", parent=parent)
        response = self.client.get("/api/categories/", {"parent": parent.id})
        assert response.status_code == 200
        assert all(c["parent"] == parent.id for c in response.json())

    def test_by_depth(self):
        root = Category.objects.create(name="R", description="Z")
        mid = Category.objects.create(name="M", description="Y", parent=root)
        leaf = Category.objects.create(name="L", description="X", parent=mid)
        response = self.client.get("/api/categories/?depth=2")
        assert response.status_code == 200
        ids = [c["id"] for c in response.json()]
        assert leaf.id in ids


@pytest.mark.django_db
class TestSimilarityRules:
    def setup_method(self):
        self.client = APIClient()

    def test_self_similarity_disallowed(self):
        c = Category.objects.create(name="Loop", description="Bad")
        response = self.client.post("/api/similarities/", {
            "category_a": c.id,
            "category_b": c.id
        }, format="json")
        assert response.status_code == 400

    def test_duplicate_similarity_is_idempotent(self):
        a = Category.objects.create(name="A", description="X")
        b = Category.objects.create(name="B", description="Y")
        self.client.post("/api/similarities/", {
            "category_a": a.id,
            "category_b": b.id
        }, format="json")
        resp = self.client.post("/api/similarities/", {
            "category_a": b.id,
            "category_b": a.id
        }, format="json")
        assert resp.status_code in (200, 201)
