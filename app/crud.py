# app/crud.py
"""
CRUD = Create, Read, Update, Delete

Beginner notes:
- These functions talk to the database
- main.py calls these to keep code clean
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select

from . import models, schemas


def get_items(db: Session) -> list[models.Item]:
    # SELECT * FROM items ORDER BY id DESC
    stmt = select(models.Item).order_by(models.Item.id.desc())
    return list(db.execute(stmt).scalars().all())


def get_item(db: Session, item_id: int) -> models.Item | None:
    # SELECT * FROM items WHERE id = item_id
    stmt = select(models.Item).where(models.Item.id == item_id)
    return db.execute(stmt).scalars().first()


def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    new_item = models.Item(
        name=item.name.strip(),
        sku=item.sku.strip(),
        qty=item.qty,
        price=item.price,
    )
    db.add(new_item)
    db.commit()       # save changes
    db.refresh(new_item)  # reload from DB (gets the ID)
    return new_item


def update_item(db: Session, item_id: int, patch: schemas.ItemUpdate) -> models.Item | None:
    obj = get_item(db, item_id)
    if not obj:
        return None

    # Only update fields that user sent
    if patch.name is not None:
        obj.name = patch.name.strip()
    if patch.sku is not None:
        obj.sku = patch.sku.strip()
    if patch.qty is not None:
        obj.qty = patch.qty
    if patch.price is not None:
        obj.price = patch.price

    db.commit()
    db.refresh(obj)
    return obj


def delete_item(db: Session, item_id: int) -> bool:
    obj = get_item(db, item_id)
    if not obj:
        return False

    db.delete(obj)
    db.commit()
    return True


