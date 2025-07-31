import nested_admin
from django.contrib import admin
from django.db import models
from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html

from catalog.graph_analysis import export_graph_analysis_to_json
from .models import Category, SimilarCategory

def view_similar_links(obj):
    url = reverse("admin:catalog_similarcategory_changelist") + f"?category_a__id__exact={obj.id}"
    return format_html("<a href='{}' target='_blank'>View all</a>", url)


view_similar_links.short_description = "All Similar"


@admin.register(Category)
class CategoryAdmin(nested_admin.NestedModelAdmin):
    list_display = ["id", "name", "parent", view_similar_links]
    search_fields = ["name", "description"]
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

    def similar_to(self, obj):
        if not obj.id:
            return "Save the category to view similar links."

        # Get all SimilarCategory where obj is involved
        links = SimilarCategory.objects.filter(
            models.Q(category_a=obj) | models.Q(category_b=obj)
        )

        # Pull out the "other" category in each pair
        related_ids = {
            link.category_b.id if link.category_a == obj else link.category_a.id
            for link in links
        }

        if not related_ids:
            return "—"

        names = Category.objects.filter(id__in=related_ids).values_list("name", flat=True)
        return ", ".join(sorted(names))

    similar_to.short_description = "Similar To"

    readonly_fields = ["similar_to"]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "—"

    image_preview.short_description = "Preview"

    readonly_fields = ["image_preview"]


@admin.register(SimilarCategory)
class SimilarCategoryAdmin(admin.ModelAdmin):
    list_display = ["category_a", "category_b"]
    autocomplete_fields = ["category_a", "category_b"]
    search_fields = ["category_a__name", "category_b__name"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


# Admin view to return graph report JSON or download it
def graph_analysis_report_view(request):
    path, data = export_graph_analysis_to_json()

    if request.GET.get("download") == "1":
        with open(path, "r") as f:
            response = HttpResponse(f.read(), content_type="application/json")
            response["Content-Disposition"] = "attachment; filename=graph_report.json"
            return response

    return JsonResponse(data, json_dumps_params={"indent": 2})


# Save the original method first
original_get_urls = admin.site.get_urls


# Add the custom view to the admin site's URLs
def custom_admin_urls():
    return [
        path("export-graph-report/", admin.site.admin_view(graph_analysis_report_view), name="graph_report")
    ] + original_get_urls()


admin.site.get_urls = custom_admin_urls
