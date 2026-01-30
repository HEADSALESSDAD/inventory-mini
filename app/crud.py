# app/crud.py
"""
CRUD یعنی:
C = Create (ساخت)
R = Read (خواندن)
U = Update (ویرایش)
D = Delete (حذف)
"""

from sqlalchemy.orm import Session
from . import models, schemas

def create_item(db: Session, item: schemas.ItemCreate):
    # یک رکورد جدید می‌سازیم
    db_item = models.Item(
        name=item.name,
        sku=item.sku,
        qty=item.qty,
        price=item.price
    )
    db.add(db_item)      # اضافه به session
    db.commit()          # ذخیره در دیتابیس
    db.refresh(db_item)  # گرفتن id ساخته شده
    return db_item

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def update_item(db: Session, item_id: int, data: schemas.ItemUpdate):
    db_item = get_item(db, item_id)
    if not db_item:
        return None

    # فقط فیلدهایی که کاربر داده را آپدیت می‌کنیم
    if data.name is not None:
        db_item.name = data.name
    if data.sku is not None:
        db_item.sku = data.sku
    if data.qty is not None:
        db_item.qty = data.qty
    if data.price is not None:
        db_item.price = data.price

    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    if not db_item:
        return None

    db.delete(db_item)
    db.commit()
    return db_item
