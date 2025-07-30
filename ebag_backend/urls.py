from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path

urlpatterns = [
    path('nested_admin/', include('nested_admin.urls')),
    path("admin/", admin.site.urls),
    path("api/", include("catalog.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
