"""REST endpoints for the FastAPI service — identical paths to Django."""
# Core
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
# Local
from .database import get_db
from .models import BusinessItem, serialize
from .schemas import BusinessItemInput, BusinessItemUpdate

router = APIRouter(prefix="/api")


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        count = db.scalar(select(BusinessItem.id).limit(1))
        total = len(db.scalars(select(BusinessItem.id)).all())
        db_ok = True
    except Exception:  # noqa: BLE001
        total = None
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "fastapi",
        "database": db_ok,
        "items": total,
    }


@router.get("/items")
def list_items(
    country: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    stmt = select(BusinessItem).order_by(BusinessItem.updated_at.desc())
    if country:
        stmt = stmt.where(BusinessItem.country == country)
    if status:
        stmt = stmt.where(BusinessItem.status == status)
    if search:
        stmt = stmt.where(BusinessItem.name.ilike(f"%{search}%"))
    return [serialize(item) for item in db.scalars(stmt).all()]


@router.get("/items/{item_id}")
def get_item(item_id: str, db: Session = Depends(get_db)):
    item = db.get(BusinessItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return serialize(item)


@router.post("/items", status_code=201)
def create_item(payload: BusinessItemInput, db: Session = Depends(get_db)):
    item = BusinessItem(
        name=payload.name,
        country=payload.country,
        status=payload.status,
        revenue=payload.revenue,
        owner=payload.owner,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize(item)


@router.patch("/items/{item_id}")
def update_item(
    item_id: str, payload: BusinessItemUpdate, db: Session = Depends(get_db)
):
    item = db.get(BusinessItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(item, field, value)
    item.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return serialize(item)


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: str, db: Session = Depends(get_db)):
    item = db.get(BusinessItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return Response(status_code=204)
