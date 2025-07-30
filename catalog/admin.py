import nested_admin
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Category, SimilarCategory


class SimilarCategoryInline(nested_admin.NestedTabularInline):
    model = SimilarCategory
    fk_name = "category_a"
    extra = 1
    autocomplete_fields = ["category_b"]
    verbose_name = "Similar to"
    verbose_name_plural = "Similar categories"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match.view_name.endswith("change"):
            return qs  # full queryset for admin filters to work
        return qs.none()  # limit to top 20 for performance


class ChildCategoryInline(nested_admin.NestedTabularInline):
    model = Category
    extra = 1
    fk_name = 'parent'
    inlines = [SimilarCategoryInline]
    show_change_link = True
    autocomplete_fields = ["parent"]


def view_similar_links(obj):
    url = reverse("admin:catalog_similarcategory_changelist") + f"?category_a__id__exact={obj.id}"
    return format_html("<a href='{}' target='_blank'>View all</a>", url)

view_similar_links.short_description = "All Similar"


@admin.register(Category)
class CategoryAdmin(nested_admin.NestedModelAdmin):
    list_display = ["id", "name", "parent", view_similar_links]
    search_fields = ["name", "description"]
    inlines = [ChildCategoryInline, SimilarCategoryInline]
    autocomplete_fields = ["parent"]

    def get_urls(self):
        default_urls = super().get_urls()
        custom_urls = [
            path(
                "tree-view/",
                self.admin_site.admin_view(self.category_tree_view),
                name="category_tree_view",
            )
        ]
        return custom_urls + default_urls

    def category_tree_view(self, request):
        return TemplateResponse(request, "admin/category_tree_admin.html", {})


@admin.register(SimilarCategory)
class SimilarCategoryAdmin(admin.ModelAdmin):
    list_display = ["category_a", "category_b"]
    autocomplete_fields = ["category_a", "category_b"]
    search_fields = ["category_a__name", "category_b__name"]
