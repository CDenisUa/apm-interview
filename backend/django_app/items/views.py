"""REST views (DRF) + health check for the Django service."""
# Core
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
# Local
from .models import BusinessItem
from .serializers import BusinessItemSerializer


class BusinessItemViewSet(viewsets.ModelViewSet):
    """CRUD for business items with country / status / search filtering."""

    serializer_class = BusinessItemSerializer

    def get_queryset(self):
        qs = BusinessItem.objects.all().order_by("-updated_at")
        params = self.request.query_params
        country = params.get("country")
        status = params.get("status")
        search = params.get("search")
        if country:
            qs = qs.filter(country=country)
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def perform_create(self, serializer):
        serializer.save(updated_at=timezone.now())

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())


@api_view(["GET"])
def health(_request):
    """Liveness + DB connectivity check."""
    try:
        count = BusinessItem.objects.count()
        db_ok = True
    except Exception:  # noqa: BLE001 — report degraded instead of crashing.
        count = None
        db_ok = False
    return Response(
        {
            "status": "ok" if db_ok else "degraded",
            "service": "django",
            "database": db_ok,
            "items": count,
        }
    )
