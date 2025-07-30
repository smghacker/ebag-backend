from rest_framework.routers import DefaultRouter
from django.urls import path, include
from catalog.views import CategoryViewSet, SimilarCategoryViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("similarities", SimilarCategoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
