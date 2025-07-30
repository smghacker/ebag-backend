from __future__ import annotations

import os
from typing import Optional

from PIL import Image
from django.core.exceptions import ValidationError
from django.db import models


def validate_image_size(image):
    max_size = 1 * 1024 * 1024  # 1MB
    if image.size > max_size:
        raise ValidationError("Image size should not exceed 1MB.")


def get_default_image():
    return "category_images/default.png"  # Place this file under MEDIA_ROOT/category_images/


def create_thumbnail(image_path):
    size = (100, 100)
    thumb_path = image_path.replace(".png", "_thumb.png").replace(".jpg", "_thumb.jpg")
    with Image.open(image_path) as img:
        img.thumbnail(size)
        img.save(thumb_path)
    return os.path.basename(thumb_path)


class Category(models.Model):
    name: str = models.CharField(max_length=255)
    description: str = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="category_images/",
        blank=True,
        null=True,
        validators=[validate_image_size],
        default=get_default_image
    )
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and os.path.exists(self.image.path):
            create_thumbnail(self.image.path)

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
            thumb_path = self.image.path.replace(".png", "_thumb.png").replace(".jpg", "_thumb.jpg")
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        super().delete(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["parent"]),
        ]
        unique_together = ("name", "parent")
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
