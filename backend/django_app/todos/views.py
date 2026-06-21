"""Full-featured Todo REST API (DRF): CRUD, pagination, filtering, sorting,
bulk operations and stats."""
# Core
import math
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Local
from .models import Todo
from .serializers import TodoSerializer

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20

# camelCase sort key -> ORM field. `priority` is handled separately (semantic).
SORT_FIELDS = {
    "createdAt": "created_at",
    "updatedAt": "updated_at",
    "dueDate": "due_date",
    "title": "title",
}


def _parse_bool(value):
    if value is None:
        return None
    return value.lower() in ("1", "true", "yes")


class TodoViewSet(viewsets.ModelViewSet):
    """CRUD + pagination + filtering + sorting + bulk ops + stats.

    Standard routes (from ModelViewSet):
        GET    /api/todos            list (paginated envelope)
        POST   /api/todos            create
        GET    /api/todos/{id}       retrieve
        PUT    /api/todos/{id}       full update
        PATCH  /api/todos/{id}       partial update
        DELETE /api/todos/{id}       delete
    Extra actions:
        GET    /api/todos/stats            counts summary
        POST   /api/todos/mark-all         { "completed": bool }
        POST   /api/todos/clear-completed  delete all completed
        POST   /api/todos/bulk-delete      { "ids": [...] }
        POST   /api/todos/{id}/toggle      flip completed
    """

    serializer_class = TodoSerializer

    # --- filtering --------------------------------------------------------
    def _filtered(self):
        qs = Todo.objects.all()
        params = self.request.query_params
        completed = _parse_bool(params.get("completed"))
        priority = params.get("priority")
        search = params.get("search")
        overdue = _parse_bool(params.get("overdue"))
        if completed is not None:
            qs = qs.filter(completed=completed)
        if priority:
            qs = qs.filter(priority=priority)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if overdue:
            qs = qs.filter(completed=False, due_date__lt=timezone.now())
        return qs

    # --- sorting ----------------------------------------------------------
    def get_queryset(self):
        qs = self._filtered()
        params = self.request.query_params
        sort_by = params.get("sort_by", "createdAt")
        descending = params.get("order", "asc").lower() == "desc"

        if sort_by == "priority":
            # Semantic order high > medium > low (not alphabetical).
            qs = qs.annotate(
                _pw=Case(
                    When(priority="high", then=Value(0)),
                    When(priority="medium", then=Value(1)),
                    When(priority="low", then=Value(2)),
                    default=Value(3),
                    output_field=IntegerField(),
                )
            )
            field = "_pw"
        else:
            field = SORT_FIELDS.get(sort_by, "created_at")

        primary = f"-{field}" if descending else field
        # `id` tiebreaker keeps pagination stable when sort values tie.
        return qs.order_by(primary, "id")

    # --- paginated list ---------------------------------------------------
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        total = qs.count()
        try:
            page = max(int(request.query_params.get("page", 1)), 1)
        except ValueError:
            page = 1
        try:
            page_size = int(request.query_params.get("page_size", DEFAULT_PAGE_SIZE))
        except ValueError:
            page_size = DEFAULT_PAGE_SIZE
        page_size = min(max(page_size, 1), MAX_PAGE_SIZE)

        start = (page - 1) * page_size
        data = TodoSerializer(qs[start : start + page_size], many=True).data
        return Response(
            {
                "items": data,
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": math.ceil(total / page_size) if page_size else 0,
            }
        )

    def perform_create(self, serializer):
        now = timezone.now()
        serializer.save(created_at=now, updated_at=now)

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())

    # --- extra actions ----------------------------------------------------
    @action(detail=False, methods=["get"])
    def stats(self, request):
        qs = Todo.objects.all()
        now = timezone.now()
        total = qs.count()
        completed = qs.filter(completed=True).count()
        overdue = qs.filter(completed=False, due_date__lt=now).count()
        return Response(
            {
                "total": total,
                "active": total - completed,
                "completed": completed,
                "overdue": overdue,
                "byPriority": {
                    "low": qs.filter(priority="low").count(),
                    "medium": qs.filter(priority="medium").count(),
                    "high": qs.filter(priority="high").count(),
                },
            }
        )

    @action(detail=False, methods=["post"], url_path="mark-all")
    def mark_all(self, request):
        completed = bool(request.data.get("completed", True))
        updated = Todo.objects.all().update(
            completed=completed, updated_at=timezone.now()
        )
        return Response({"updated": updated})

    @action(detail=False, methods=["post"], url_path="clear-completed")
    def clear_completed(self, request):
        deleted, _ = Todo.objects.filter(completed=True).delete()
        return Response({"deleted": deleted})

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        if not isinstance(ids, list):
            return Response(
                {"detail": "`ids` must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted, _ = Todo.objects.filter(id__in=ids).delete()
        return Response({"deleted": deleted})

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        todo = Todo.objects.filter(id=pk).first()
        if todo is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        todo.completed = not todo.completed
        todo.updated_at = timezone.now()
        todo.save()
        return Response(TodoSerializer(todo).data)
