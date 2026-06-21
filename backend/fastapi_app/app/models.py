"""SQLAlchemy model mapped onto the shared `business_items` table."""
# Core
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, Numeric, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
# Local
from .database import Base


def _iso(value) -> Optional[str]:
    """ISO-8601 with a trailing Z (matches the Django service byte-for-byte)."""
    return value.isoformat().replace("+00:00", "Z") if value else None


class BusinessItem(Base):
    __tablename__ = "business_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    revenue: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


def serialize(item: BusinessItem) -> dict:
    """Single source of the JSON shape — identical to the Django serializer."""
    return {
        "id": str(item.id),
        "name": item.name,
        "country": item.country,
        "status": item.status,
        "revenue": float(item.revenue),
        # Normalise to a trailing "Z" so the timestamp string matches the
        # Django service byte-for-byte (both are the same UTC instant).
        "updatedAt": _iso(item.updated_at),
        "owner": item.owner,
    }


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="medium")
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


def serialize_todo(t: "Todo") -> dict:
    """Single source of the Todo JSON shape — identical to the Django serializer."""
    return {
        "id": str(t.id),
        "title": t.title,
        "description": t.description,
        "completed": t.completed,
        "priority": t.priority,
        "dueDate": _iso(t.due_date),
        "createdAt": _iso(t.created_at),
        "updatedAt": _iso(t.updated_at),
    }
