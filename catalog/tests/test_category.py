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
