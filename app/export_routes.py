# app/export_routes.py
"""
هدف:
- ساخت endpoint های دانلود Excel و PDF
- فعلاً برای items می‌زنیم
- بعداً برای هر بخش دیگری هم همین الگو را تکرار می‌کنی
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .db import SessionLocal
from . import crud
from .exporters import build_excel_xlsx, build_pdf_a4


router = APIRouter(tags=["Export"])


def get_db():
    """
    دیتابیس Session می‌سازیم و بعد از درخواست می‌بندیم.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/export/items.xlsx")
def export_items_excel(db: Session = Depends(get_db)):
    """
    خروجی Excel برای آیتم‌ها
    """
    items = crud.get_items(db)

    headers = ["ID", "Name", "Qty"]
    rows = [[it.id, it.name, it.qty] for it in items]

    bio = build_excel_xlsx(title="Items", headers=headers, rows=rows)

    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=items.xlsx"},
    )


@router.get("/export/items.pdf")
def export_items_pdf(db: Session = Depends(get_db)):
    """
    خروجی PDF (A4) برای آیتم‌ها
    """
    items = crud.get_items(db)

    headers = ["ID", "Name", "Qty"]
    rows = [[it.id, it.name, it.qty] for it in items]

    bio = build_pdf_a4(title="Items Report (A4)", headers=headers, rows=rows)

    return StreamingResponse(
        bio,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=items.pdf"},
    )
