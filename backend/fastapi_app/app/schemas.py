"""Pydantic request models for the REST layer."""
# Core
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel

Priority = Literal["low", "medium", "high"]


class BusinessItemInput(BaseModel):
    """Full payload for create (POST)."""

    name: str
    country: str
    status: str
    revenue: float = 0
    owner: str


class BusinessItemUpdate(BaseModel):
    """Partial payload for update (PATCH) — every field optional."""

    name: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None
    revenue: Optional[float] = None
    owner: Optional[str] = None


class TodoInput(BaseModel):
    """Full payload for create (POST) / full update (PUT)."""

    title: str
    description: str = ""
    completed: bool = False
    priority: Priority = "medium"  # invalid value -> 422
    dueDate: Optional[datetime] = None


class TodoUpdate(BaseModel):
    """Partial payload for update (PATCH) — every field optional."""

    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    dueDate: Optional[datetime] = None


class MarkAllInput(BaseModel):
    completed: bool = True


class BulkDeleteInput(BaseModel):
    ids: list[str]
