from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import AirlineViewSet, AirportViewSet, FlightViewSet, TurnaroundViewSet

# DRF Router configuration
router = DefaultRouter()
router.register(r"airlines", AirlineViewSet)
router.register(r"airports", AirportViewSet)
router.register(r"flights", FlightViewSet)
router.register(r"turnarounds", TurnaroundViewSet)

# Main URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    # API Routes
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
