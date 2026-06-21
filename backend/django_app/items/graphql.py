"""
GraphQL schema (strawberry) for the Django service.

The GraphQL type and the REST serializer expose the SAME shape:
    id, name, country, status, revenue, updatedAt, owner
and the FastAPI service mirrors this schema 1:1.
"""
# Core
from typing import Optional
import strawberry
from django.utils import timezone
# Local
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
        qs = BusinessItemModel.objects.all().order_by("-updated_at")
        if country:
            qs = qs.filter(country=country)
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(name__icontains=search)
        return [_to_gql(m) for m in qs]

    @strawberry.field
    def item(self, id: strawberry.ID) -> Optional[BusinessItem]:
        m = BusinessItemModel.objects.filter(id=id).first()
        return _to_gql(m) if m else None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_item(self, input: BusinessItemInput) -> BusinessItem:
        m = BusinessItemModel.objects.create(
            name=input.name,
            country=input.country,
            status=input.status,
            revenue=input.revenue,
            owner=input.owner,
            updated_at=timezone.now(),
        )
        return _to_gql(m)

    @strawberry.mutation
    def update_item(
        self, id: strawberry.ID, input: BusinessItemInput
    ) -> Optional[BusinessItem]:
        m = BusinessItemModel.objects.filter(id=id).first()
        if not m:
            return None
        m.name = input.name
        m.country = input.country
        m.status = input.status
        m.revenue = input.revenue
        m.owner = input.owner
        m.updated_at = timezone.now()
        m.save()
        return _to_gql(m)

    @strawberry.mutation
    def delete_item(self, id: strawberry.ID) -> bool:
        deleted, _ = BusinessItemModel.objects.filter(id=id).delete()
        return deleted > 0


schema = strawberry.Schema(query=Query, mutation=Mutation)
