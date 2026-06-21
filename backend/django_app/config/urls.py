"""URL routing for the Django service — REST + GraphQL + health."""
# Core
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import SimpleRouter
from strawberry.django.views import GraphQLView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
# Local
from items.views import BusinessItemViewSet, health
from todos.views import TodoViewSet
from config.schema import schema


def root(_request):
    return JsonResponse(
        {
            "service": "django",
            "endpoints": {
                "health": "/api/health",
                "rest_items": "/api/items",
                "rest_todos": "/api/todos",
                "graphql": "/graphql",
                "docs": "/api/docs",
                "openapi_schema": "/api/schema",
            },
        }
    )


# trailing_slash=False keeps the paths identical to the FastAPI service.
router = SimpleRouter(trailing_slash=False)
router.register("api/items", BusinessItemViewSet, basename="items")
router.register("api/todos", TodoViewSet, basename="todos")

urlpatterns = [
    path("", root),
    path("api/health", health),
    # OpenAPI schema + Swagger UI (the FastAPI-style /docs experience).
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("graphql", csrf_exempt(GraphQLView.as_view(schema=schema))),
    *router.urls,
]
