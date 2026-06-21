"""
GraphQL schema (strawberry) for the FastAPI service.

Mirrors the Django GraphQL schema 1:1 — same types, same queries, same
mutations — so a single frontend GraphQL document works against either server.
"""
# Core
from datetime import datetime, timezone
from typing import Optional
import strawberry
from sqlalchemy import select
# Local
from .database import SessionLocal
from .models import BusinessItem as BusinessItemModel


@strawberry.type
class BusinessItem:
    id: strawberry.ID
    name: str
    country: str
    status: str
    revenue: float
    updatedAt: str
    owner: str


@strawberry.input
class BusinessItemInput:
    name: str
    country: str
    status: str
    revenue: float
    owner: str


def _to_gql(m: BusinessItemModel) -> BusinessItem:
    return BusinessItem(
        id=str(m.id),
        name=m.name,
        country=m.country,
        status=m.status,
        revenue=float(m.revenue),
        updatedAt=m.updated_at.isoformat().replace("+00:00", "Z"),
        owner=m.owner,
    )


@strawberry.type
class Query:
    @strawberry.field
    def items(
        self,
        country: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[BusinessItem]:
        with SessionLocal() as db:
            stmt = select(BusinessItemModel).order_by(
                BusinessItemModel.updated_at.desc()
            )
            if country:
                stmt = stmt.where(BusinessItemModel.country == country)
            if status:
                stmt = stmt.where(BusinessItemModel.status == status)
            if search:
                stmt = stmt.where(BusinessItemModel.name.ilike(f"%{search}%"))
            return [_to_gql(m) for m in db.scalars(stmt).all()]

    @strawberry.field
    def item(self, id: strawberry.ID) -> Optional[BusinessItem]:
        with SessionLocal() as db:
            m = db.get(BusinessItemModel, id)
            return _to_gql(m) if m else None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_item(self, input: BusinessItemInput) -> BusinessItem:
        with SessionLocal() as db:
            m = BusinessItemModel(
                name=input.name,
                country=input.country,
                status=input.status,
                revenue=input.revenue,
                owner=input.owner,
                updated_at=datetime.now(timezone.utc),
            )
            db.add(m)
            db.commit()
            db.refresh(m)
            return _to_gql(m)

    @strawberry.mutation
    def update_item(
        self, id: strawberry.ID, input: BusinessItemInput
    ) -> Optional[BusinessItem]:
        with SessionLocal() as db:
            m = db.get(BusinessItemModel, id)
            if not m:
                return None
            m.name = input.name
            m.country = input.country
            m.status = input.status
            m.revenue = input.revenue
            m.owner = input.owner
            m.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(m)
            return _to_gql(m)

    @strawberry.mutation
    def delete_item(self, id: strawberry.ID) -> bool:
        with SessionLocal() as db:
            m = db.get(BusinessItemModel, id)
            if not m:
                return False
            db.delete(m)
            db.commit()
            return True


# Items-only schema kept for reference; the app uses the merged schema in
# app/schema.py (items + todos).
schema = strawberry.Schema(query=Query, mutation=Mutation)
