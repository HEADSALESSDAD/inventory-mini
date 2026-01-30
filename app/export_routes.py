# app/export_routes.py
"""
Export routes

Beginner notes:
- /reports shows a page with download buttons
- /export/items.xlsx downloads Excel
- /export/items.pdf downloads PDF (A4)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlalchemy.orm import Session

from .db import SessionLocal
from . import crud
from .export_utils import items_to_xlsx_bytes, items_to_pdf_bytes, make_export_filename

router = APIRouter(tags=["Exports"])


def get_db():
    """Same idea as in main.py: open DB session, close after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/reports", response_class=HTMLResponse)
def reports_page():
    # Simple HTML (we keep it super simple)
    return """
    <html>
      <head><title>Reports</title></head>
      <body style="font-family: Arial; padding: 24px;">
        <h2>Reports</h2>
        <p>Download Inventory exports:</p>
        <ul>
          <li><a href="/export/items.xlsx">Download Excel (XLSX)</a></li>
          <li><a href="/export/items.pdf">Download PDF (A4)</a></li>
        </ul>
        <p><a href="/">Back to Dashboard</a></p>
      </body>
    </html>
    """


@router.get("/export/items.xlsx")
def export_items_xlsx(db: Session = Depends(get_db)):
    items = crud.get_items(db)
    payload = [
        {"id": i.id, "name": i.name, "sku": i.sku, "qty": i.qty, "price": float(i.price) if i.price is not None else None}
        for i in items
    ]

    content = items_to_xlsx_bytes(payload)
    filename = make_export_filename("inventory_items", "xlsx")

    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/items.pdf")
def export_items_pdf(db: Session = Depends(get_db)):
    items = crud.get_items(db)
    payload = [
        {"id": i.id, "name": i.name, "sku": i.sku, "qty": i.qty, "price": float(i.price) if i.price is not None else None}
        for i in items
    ]

    content = items_to_pdf_bytes(payload)
    filename = make_export_filename("inventory_items_A4", "pdf")

    return StreamingResponse(
        iter([content]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
