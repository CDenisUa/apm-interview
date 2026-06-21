"""GraphQL schema parts (strawberry) for todos — merged into the root schema."""
# Core
import math
from datetime import datetime, timezone
from typing import Optional
import strawberry
from sqlalchemy import select, func, case, or_, update as sql_update, delete as sql_delete
# Local
from .database import SessionLocal
from .models import Todo as TodoModel, _iso

MAX_PAGE_SIZE = 100

SORT_COLUMNS = {
    "createdAt": TodoModel.created_at,
    "updatedAt": TodoModel.updated_at,
    "dueDate": TodoModel.due_date,
    "title": TodoModel.title,
}

PRIORITY_WEIGHT = case(
    (TodoModel.priority == "high", 0),
    (TodoModel.priority == "medium", 1),
    (TodoModel.priority == "low", 2),
    else_=3,
)


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


def _parse_due(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _filtered(stmt, completed, priority, search, overdue):
    if completed is not None:
        stmt = stmt.where(TodoModel.completed == completed)
    if priority:
        stmt = stmt.where(TodoModel.priority == priority)
    if search:
        stmt = stmt.where(
            or_(
                TodoModel.title.ilike(f"%{search}%"),
                TodoModel.description.ilike(f"%{search}%"),
            )
        )
    if overdue:
        stmt = stmt.where(
            TodoModel.completed.is_(False),
            TodoModel.due_date < datetime.now(timezone.utc),
        )
    return stmt


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
        page = max(page, 1)
        page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
        sort_col = (
            PRIORITY_WEIGHT
            if sort_by == "priority"
            else SORT_COLUMNS.get(sort_by, TodoModel.created_at)
        )
        direction = sort_col.desc() if order.lower() == "desc" else sort_col.asc()
        with SessionLocal() as db:
            total = (
                db.scalar(
                    _filtered(
                        select(func.count()).select_from(TodoModel),
                        completed,
                        priority,
                        search,
                        overdue,
                    )
                )
                or 0
            )
            stmt = _filtered(select(TodoModel), completed, priority, search, overdue)
            stmt = stmt.order_by(direction, TodoModel.id)
            stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            items = [_to_gql(m) for m in db.scalars(stmt).all()]
        return TodoPage(
            items=items,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=math.ceil(total / page_size) if page_size else 0,
        )

    @strawberry.field
    def todo(self, id: strawberry.ID) -> Optional[Todo]:
        with SessionLocal() as db:
            m = db.get(TodoModel, id)
            return _to_gql(m) if m else None

    @strawberry.field
    def todo_stats(self) -> TodoStats:
        now = datetime.now(timezone.utc)
        with SessionLocal() as db:
            total = db.scalar(select(func.count()).select_from(TodoModel)) or 0
            completed = (
                db.scalar(
                    select(func.count())
                    .select_from(TodoModel)
                    .where(TodoModel.completed.is_(True))
                )
                or 0
            )
            overdue = (
                db.scalar(
                    select(func.count())
                    .select_from(TodoModel)
                    .where(TodoModel.completed.is_(False), TodoModel.due_date < now)
                )
                or 0
            )

            def by(p):
                return (
                    db.scalar(
                        select(func.count())
                        .select_from(TodoModel)
                        .where(TodoModel.priority == p)
                    )
                    or 0
                )

            return TodoStats(
                total=total,
                active=total - completed,
                completed=completed,
                overdue=overdue,
                byPriority=PriorityCounts(
                    low=by("low"), medium=by("medium"), high=by("high")
                ),
            )


@strawberry.type
class TodoMutation:
    @strawberry.mutation
    def create_todo(self, input: TodoInput) -> Todo:
        now = datetime.now(timezone.utc)
        with SessionLocal() as db:
            m = TodoModel(
                title=input.title,
                description=input.description,
                completed=input.completed,
                priority=input.priority,
                due_date=_parse_due(input.dueDate),
                created_at=now,
                updated_at=now,
            )
            db.add(m)
            db.commit()
            db.refresh(m)
            return _to_gql(m)

    @strawberry.mutation
    def update_todo(self, id: strawberry.ID, input: TodoInput) -> Optional[Todo]:
        with SessionLocal() as db:
            m = db.get(TodoModel, id)
            if not m:
                return None
            m.title = input.title
            m.description = input.description
            m.completed = input.completed
            m.priority = input.priority
            m.due_date = _parse_due(input.dueDate)
            m.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(m)
            return _to_gql(m)

    @strawberry.mutation
    def toggle_todo(self, id: strawberry.ID) -> Optional[Todo]:
        with SessionLocal() as db:
            m = db.get(TodoModel, id)
            if not m:
                return None
            m.completed = not m.completed
            m.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(m)
            return _to_gql(m)

    @strawberry.mutation
    def delete_todo(self, id: strawberry.ID) -> bool:
        with SessionLocal() as db:
            m = db.get(TodoModel, id)
            if not m:
                return False
            db.delete(m)
            db.commit()
            return True

    @strawberry.mutation
    def mark_all(self, completed: bool = True) -> int:
        with SessionLocal() as db:
            result = db.execute(
                sql_update(TodoModel).values(
                    completed=completed, updated_at=datetime.now(timezone.utc)
                )
            )
            db.commit()
            return result.rowcount

    @strawberry.mutation
    def clear_completed(self) -> int:
        with SessionLocal() as db:
            result = db.execute(
                sql_delete(TodoModel).where(TodoModel.completed.is_(True))
            )
            db.commit()
            return result.rowcount

    @strawberry.mutation
    def bulk_delete_todos(self, ids: list[strawberry.ID]) -> int:
        with SessionLocal() as db:
            result = db.execute(
                sql_delete(TodoModel).where(TodoModel.id.in_(ids))
            )
            db.commit()
            return result.rowcount
