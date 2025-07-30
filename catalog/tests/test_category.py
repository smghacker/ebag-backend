import pytest
from django.core.exceptions import ValidationError

from catalog.models import Category


@pytest.mark.django_db
def test_category_depth():
    root = Category.objects.create(name="Root")
    child = Category.objects.create(name="Child", parent=root)
    grandchild = Category.objects.create(name="Grandchild", parent=child)

    assert root.depth == 0
    assert child.depth == 1
    assert grandchild.depth == 2


@pytest.mark.django_db
def test_move_to_another_parent():
    a = Category.objects.create(name="A")
    b = Category.objects.create(name="B")
    c = Category.objects.create(name="C", parent=a)

    c.move_to(b)
    c.refresh_from_db()
    assert c.parent == b
    assert c.depth == 1


@pytest.mark.django_db
def test_cannot_move_to_self():
    a = Category.objects.create(name="A")
    with pytest.raises(ValidationError):
        a.move_to(a)


@pytest.mark.django_db
def test_cannot_create_loop():
    root = Category.objects.create(name="Root")
    child = Category.objects.create(name="Child", parent=root)
    grandchild = Category.objects.create(name="Grandchild", parent=child)

    # Try to move root under grandchild (loop)
    with pytest.raises(ValidationError):
        root.move_to(grandchild)
