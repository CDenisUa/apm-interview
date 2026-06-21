"""Full-featured Todo REST API (FastAPI): CRUD, pagination, filtering,
sorting, bulk operations and stats.

NOTE: static collection routes (/todos/stats, /todos/mark-all, ...) are
declared BEFORE the dynamic /todos/{todo_id} route so they are matched first.
"""
# Core
import math
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select, func, update as sql_update, delete as sql_delete, case, or_
from sqlalchemy.orm import Session
# Local
from .database import get_db
from .models import Todo, serialize_todo
from .schemas import TodoInput, TodoUpdate, MarkAllInput, BulkDeleteInput

router = APIRouter(prefix="/api")

MAX_PAGE_SIZE = 100

SORT_COLUMNS = {
    "createdAt": Todo.created_at,
    "updatedAt": Todo.updated_at,
    "dueDate": Todo.due_date,
    "title": Todo.title,
}

# Semantic priority weight (high > medium > low).
PRIORITY_WEIGHT = case(
    (Todo.priority == "high", 0),
    (Todo.priority == "medium", 1),
    (Todo.priority == "low", 2),
    else_=3,
)


def _apply_filters(stmt, completed, priority, search, overdue):
    if completed is not None:
        stmt = stmt.where(Todo.completed == completed)
    if priority:
        stmt = stmt.where(Todo.priority == priority)
    if search:
        stmt = stmt.where(
            or_(Todo.title.ilike(f"%{search}%"), Todo.description.ilike(f"%{search}%"))
        )
    if overdue:
        stmt = stmt.where(
            Todo.completed.is_(False), Todo.due_date < datetime.now(timezone.utc)
        )
    return stmt


# ----------------------------- collection -----------------------------------
@router.get("/todos")
def list_todos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    overdue: Optional[bool] = None,
    sort_by: str = "createdAt",
    order: str = "asc",
    db: Session = Depends(get_db),
):
    total = db.scalar(
        _apply_filters(
            select(func.count()).select_from(Todo),
            completed,
            priority,
            search,
            overdue,
        )
    ) or 0

    sort_col = PRIORITY_WEIGHT if sort_by == "priority" else SORT_COLUMNS.get(
        sort_by, Todo.created_at
    )
    direction = sort_col.desc() if order.lower() == "desc" else sort_col.asc()

    stmt = _apply_filters(select(Todo), completed, priority, search, overdue)
    # `id` tiebreaker keeps pagination stable when sort values tie.
    stmt = stmt.order_by(direction, Todo.id)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    items = [serialize_todo(t) for t in db.scalars(stmt).all()]

    return {
        "items": items,
        "total": total,
        "page": page,
        "pageSize": page_size,
        "totalPages": math.ceil(total / page_size) if page_size else 0,
    }


@router.get("/todos/stats")
def todo_stats(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    total = db.scalar(select(func.count()).select_from(Todo)) or 0
    completed = db.scalar(
        select(func.count()).select_from(Todo).where(Todo.completed.is_(True))
    ) or 0
    overdue = db.scalar(
        select(func.count())
        .select_from(Todo)
        .where(Todo.completed.is_(False), Todo.due_date < now)
    ) or 0

    def by(p):
        return db.scalar(
            select(func.count()).select_from(Todo).where(Todo.priority == p)
        ) or 0

    return {
        "total": total,
        "active": total - completed,
        "completed": completed,
        "overdue": overdue,
        "byPriority": {"low": by("low"), "medium": by("medium"), "high": by("high")},
    }


@router.post("/todos", status_code=201)
def create_todo(payload: TodoInput, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    todo = Todo(
        title=payload.title,
        description=payload.description,
        completed=payload.completed,
        priority=payload.priority,
        due_date=payload.dueDate,
        created_at=now,
        updated_at=now,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return serialize_todo(todo)


@router.post("/todos/mark-all")
def mark_all(payload: MarkAllInput, db: Session = Depends(get_db)):
    result = db.execute(
        sql_update(Todo).values(
            completed=payload.completed, updated_at=datetime.now(timezone.utc)
        )
    )
    db.commit()
    return {"updated": result.rowcount}


@router.post("/todos/clear-completed")
def clear_completed(db: Session = Depends(get_db)):
    result = db.execute(sql_delete(Todo).where(Todo.completed.is_(True)))
    db.commit()
    return {"deleted": result.rowcount}


@router.post("/todos/bulk-delete")
def bulk_delete(payload: BulkDeleteInput, db: Session = Depends(get_db)):
    result = db.execute(sql_delete(Todo).where(Todo.id.in_(payload.ids)))
    db.commit()
    return {"deleted": result.rowcount}


# ------------------------------- item ---------------------------------------
@router.get("/todos/{todo_id}")
def get_todo(todo_id: str, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return serialize_todo(todo)


@router.put("/todos/{todo_id}")
def replace_todo(todo_id: str, payload: TodoInput, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.title = payload.title
    todo.description = payload.description
    todo.completed = payload.completed
    todo.priority = payload.priority
    todo.due_date = payload.dueDate
    todo.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(todo)
    return serialize_todo(todo)


@router.patch("/todos/{todo_id}")
def update_todo(todo_id: str, payload: TodoUpdate, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    data = payload.model_dump(exclude_unset=True)
    if "dueDate" in data:
        todo.due_date = data.pop("dueDate")
    for field, value in data.items():
        setattr(todo, field, value)
    todo.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(todo)
    return serialize_todo(todo)


@router.post("/todos/{todo_id}/toggle")
def toggle_todo(todo_id: str, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.completed = not todo.completed
    todo.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(todo)
    return serialize_todo(todo)


@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return Response(status_code=204)
