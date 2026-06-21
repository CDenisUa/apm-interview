"""GraphQL schema parts (strawberry) for todos — merged into the root schema."""
# Core
import math
from typing import Optional
import strawberry
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
# Local
from .models import Todo as TodoModel

MAX_PAGE_SIZE = 100

SORT_FIELDS = {
    "createdAt": "created_at",
    "updatedAt": "updated_at",
    "dueDate": "due_date",
    "title": "title",
}


@strawberry.type
class Todo:
    id: strawberry.ID
    title: str
    description: str
    completed: bool
    priority: str
    dueDate: Optional[str]
    createdAt: str
    updatedAt: str


@strawberry.type
class TodoPage:
    items: list[Todo]
    total: int
    page: int
    pageSize: int
    totalPages: int


@strawberry.input
class TodoInput:
    title: str
    description: str = ""
    completed: bool = False
    priority: str = "medium"
    dueDate: Optional[str] = None


@strawberry.type
class PriorityCounts:
    low: int
    medium: int
    high: int


@strawberry.type
class TodoStats:
    total: int
    active: int
    completed: int
    overdue: int
    byPriority: PriorityCounts


def _iso(value) -> Optional[str]:
    return value.isoformat().replace("+00:00", "Z") if value else None


def _to_gql(m: TodoModel) -> Todo:
    return Todo(
        id=str(m.id),
        title=m.title,
        description=m.description,
        completed=m.completed,
        priority=m.priority,
        dueDate=_iso(m.due_date),
        createdAt=_iso(m.created_at),
        updatedAt=_iso(m.updated_at),
    )


@strawberry.type
class TodoQuery:
    @strawberry.field
    def todos(
        self,
        page: int = 1,
        page_size: int = 20,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        overdue: Optional[bool] = None,
        sort_by: str = "createdAt",
        order: str = "asc",
    ) -> TodoPage:
        qs = TodoModel.objects.all()
        if completed is not None:
            qs = qs.filter(completed=completed)
        if priority:
            qs = qs.filter(priority=priority)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if overdue:
            qs = qs.filter(completed=False, due_date__lt=timezone.now())

        if sort_by == "priority":
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
        primary = f"-{field}" if order.lower() == "desc" else field
        qs = qs.order_by(primary, "id")

        total = qs.count()
        page = max(page, 1)
        page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
        start = (page - 1) * page_size
        items = [_to_gql(m) for m in qs[start : start + page_size]]
        return TodoPage(
            items=items,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=math.ceil(total / page_size) if page_size else 0,
        )

    @strawberry.field
    def todo(self, id: strawberry.ID) -> Optional[Todo]:
        m = TodoModel.objects.filter(id=id).first()
        return _to_gql(m) if m else None

    @strawberry.field
    def todo_stats(self) -> TodoStats:
        qs = TodoModel.objects.all()
        now = timezone.now()
        total = qs.count()
        completed = qs.filter(completed=True).count()
        overdue = qs.filter(completed=False, due_date__lt=now).count()
        return TodoStats(
            total=total,
            active=total - completed,
            completed=completed,
            overdue=overdue,
            byPriority=PriorityCounts(
                low=qs.filter(priority="low").count(),
                medium=qs.filter(priority="medium").count(),
                high=qs.filter(priority="high").count(),
            ),
        )


@strawberry.type
class TodoMutation:
    @strawberry.mutation
    def create_todo(self, input: TodoInput) -> Todo:
        now = timezone.now()
        m = TodoModel.objects.create(
            title=input.title,
            description=input.description,
            completed=input.completed,
            priority=input.priority,
            due_date=input.dueDate,
            created_at=now,
            updated_at=now,
        )
        return _to_gql(m)

    @strawberry.mutation
    def update_todo(
        self, id: strawberry.ID, input: TodoInput
    ) -> Optional[Todo]:
        m = TodoModel.objects.filter(id=id).first()
        if not m:
            return None
        m.title = input.title
        m.description = input.description
        m.completed = input.completed
        m.priority = input.priority
        m.due_date = input.dueDate
        m.updated_at = timezone.now()
        m.save()
        return _to_gql(m)

    @strawberry.mutation
    def toggle_todo(self, id: strawberry.ID) -> Optional[Todo]:
        m = TodoModel.objects.filter(id=id).first()
        if not m:
            return None
        m.completed = not m.completed
        m.updated_at = timezone.now()
        m.save()
        return _to_gql(m)

    @strawberry.mutation
    def delete_todo(self, id: strawberry.ID) -> bool:
        deleted, _ = TodoModel.objects.filter(id=id).delete()
        return deleted > 0

    @strawberry.mutation
    def mark_all(self, completed: bool = True) -> int:
        return TodoModel.objects.all().update(
            completed=completed, updated_at=timezone.now()
        )

    @strawberry.mutation
    def clear_completed(self) -> int:
        deleted, _ = TodoModel.objects.filter(completed=True).delete()
        return deleted

    @strawberry.mutation
    def bulk_delete_todos(self, ids: list[strawberry.ID]) -> int:
        deleted, _ = TodoModel.objects.filter(id__in=ids).delete()
        return deleted
