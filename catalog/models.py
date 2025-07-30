from __future__ import annotations

from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name: str = models.CharField(max_length=255)
    description: str = models.TextField(blank=True)
    image: str = models.URLField(blank=True)
    parent: Optional[Category] = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    def __str__(self):
        return self.name

    def move_to(self, new_parent: Optional[Category]) -> None:
        """Moves the category to a new parent in the tree."""
        if new_parent and self.pk == new_parent.pk:
            raise ValidationError("A category cannot be its own parent.")

        if new_parent and self._is_descendant_of(new_parent):
            raise ValidationError("Cannot move a category under its own subtree.")
        self.parent = new_parent
        self.save()

    def _is_descendant_of(self, target: Category) -> bool:
        node = target
        while node:
            if node.pk == self.pk:
                return True
            node = node.parent
        return False

    @property
    def depth(self) -> int:
        """Calculates the depth of the category in the tree."""
        depth = 0
        node = self.parent
        while node:
            depth += 1
            node = node.parent
        return depth

    class Meta:
        indexes = [
            models.Index(fields=["parent"]),
        ]
        ordering = ["name"]


class SimilarCategory(models.Model):
    category_a: Category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="similar_from"
    )
    category_b: Category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="similar_to"
    )

    def clean(self) -> None:
        if self.category_a == self.category_b:
            raise ValidationError("A category cannot be similar to itself.")
        # Ensure symmetry: always store (min_id, max_id)
        if self.category_a.id and self.category_b.id:
            if self.category_a.id > self.category_b.id:
                self.category_a, self.category_b = self.category_b, self.category_a

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category_a.name} ~ {self.category_b.name}"

    class Meta:
        unique_together = ("category_a", "category_b")
        indexes = [
            models.Index(fields=["category_a"]),
            models.Index(fields=["category_b"]),
        ]
