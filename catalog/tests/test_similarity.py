import pytest
from django.core.exceptions import ValidationError
from catalog.models import Category, SimilarCategory


@pytest.mark.django_db
def test_create_similarity():
    a = Category.objects.create(name="A")
    b = Category.objects.create(name="B")

    link = SimilarCategory.objects.create(category_a=a, category_b=b)
    assert link.category_a in (a, b)
    assert link.category_b in (a, b)
    assert link.category_a != link.category_b


@pytest.mark.django_db
def test_prevent_self_similarity():
    a = Category.objects.create(name="A")
    with pytest.raises(ValidationError):
        SimilarCategory.objects.create(category_a=a, category_b=a)


@pytest.mark.django_db
def test_symmetry_enforcement():
    a = Category.objects.create(name="A")
    b = Category.objects.create(name="B")

    link = SimilarCategory.objects.create(category_a=b, category_b=a)  # reverse order
    assert link.category_a.id < link.category_b.id  # reordered internally


@pytest.mark.django_db
def test_duplicate_similarity_blocked():
    a = Category.objects.create(name="A")
    b = Category.objects.create(name="B")

    SimilarCategory.objects.create(category_a=a, category_b=b)

    with pytest.raises(Exception):  # IntegrityError or ValidationError depending on DB/backend
        SimilarCategory.objects.create(category_a=b, category_b=a)
