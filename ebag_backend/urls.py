from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('nested_admin/', include('nested_admin.urls')),
    path("admin/", admin.site.urls),
    path("api/", include("catalog.urls")),
]
