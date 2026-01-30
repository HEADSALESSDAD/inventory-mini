# app/main.py
"""
BEGINNER-FRIENDLY MAIN FILE (FastAPI)

What this file does:
1) Creates the FastAPI app
2) Creates DB tables on startup (SQLite/Postgres)
3) Serves a clean HTML dashboard (English UI only)
4) Provides CRUD APIs for Items
5) Provides Excel + PDF (A4) export endpoints

Tip:
- "API" is for machines (Swagger /docs)
- "Dashboard" is for humans (browser UI)
"""

from typing import List, Optional

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Local project imports
from .db import SessionLocal, engine, Base
from . import schemas, crud

# If you already have export_utils, we use it.
# If you don't, comment these 2 lines and tell me, I’ll paste a self-contained exporter.
from .export_utils import items_to_xlsx_bytes, items_to_pdf_bytes, make_export_filename


# ----------------------------
# 1) Create the app
# ----------------------------
app = FastAPI(title="Inventory Mini", version="0.2.0")


# ----------------------------
# 2) Static files (CSS/JS)
# ----------------------------
# This lets your templates load: /static/css/app.css and /static/js/app.js
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates folder (HTML)
templates = Jinja2Templates(directory="app/templates")


# ----------------------------
# 3) DB session dependency
# ----------------------------
def get_db():
    """
    Creates a DB session per request, then closes it.
    Why?
    - If you don't close sessions, connections pile up and your app gets slow/broken.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# 4) Create tables on startup
# ----------------------------
@app.on_event("startup")
def on_startup():
    """
    Runs once when the server starts.
    Creates DB tables if they do not exist.
    """
    Base.metadata.create_all(bind=engine)


# ----------------------------
# 5) Health check (for Render)
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ----------------------------
# 6) Dashboard page (English UI)
# ----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    """
    Renders the dashboard HTML.
    We pass "items" to the template so the page loads instantly (no endless LOADING).
    """
    items = crud.get_items(db)
    # Simple stats for cards
    total_rows = len(items)
    total_qty = sum([int(getattr(i, "qty", 0) or 0) for i in items])
    total_value = sum(
        [
            (float(getattr(i, "price", 0) or 0) * float(getattr(i, "qty", 0) or 0))
            for i in items
        ]
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": items,
            "total_rows": total_rows,
            "total_qty": total_qty,
            "total_value": total_value,
        },
    )


# ----------------------------
# 7) API: List items
# ----------------------------
@app.get("/items", response_model=List[schemas.ItemOut])
def list_items(db: Session = Depends(get_db)):
    return crud.get_items(db)


# ----------------------------
# 8) API: Create item
# ----------------------------
@app.post("/items", response_model=schemas.ItemOut)
def add_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)


# ----------------------------
# 9) API: Get one item (optional)
# ----------------------------
@app.get("/items/{item_id}", response_model=schemas.ItemOut)
def get_one_item(item_id: int, db: Session = Depends(get_db)):
    obj = crud.get_item(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj


# ----------------------------
# 10) API: Update item
# ----------------------------
@app.put("/items/{item_id}", response_model=schemas.ItemOut)
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """
    Beginner shortcut:
    - We reuse ItemCreate schema for update.
    - Later you can make a separate ItemUpdate schema (optional fields).
    """
    obj = crud.update_item(db, item_id=item_id, item=item)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj


# ----------------------------
# 11) API: Delete item
# ----------------------------
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_item(db, item_id=item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ok": True}


# ----------------------------
# 12) Exports: Excel + PDF (A4)
# ----------------------------
@app.get("/exports/items.xlsx")
def export_items_excel(db: Session = Depends(get_db)):
    items = crud.get_items(db)

    # Convert ORM objects into simple dicts (safe for export)
    rows = []
    for i in items:
        rows.append(
            {
                "id": getattr(i, "id", None),
                "name": getattr(i, "name", ""),
                "sku": getattr(i, "sku", ""),
                "qty": getattr(i, "qty", 0),
                "price": getattr(i, "price", None),
            }
        )

    data = items_to_xlsx_bytes(rows)
    filename = make_export_filename(prefix="items", ext="xlsx")

    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/exports/items.pdf")
def export_items_pdf(db: Session = Depends(get_db)):
    items = crud.get_items(db)

    rows = []
    for i in items:
        rows.append(
            {
                "id": getattr(i, "id", None),
                "name": getattr(i, "name", ""),
                "sku": getattr(i, "sku", ""),
                "qty": getattr(i, "qty", 0),
                "price": getattr(i, "price", None),
            }
        )

    data = items_to_pdf_bytes(rows, page_size="A4")
    filename = make_export_filename(prefix="items", ext="pdf")

    return StreamingResponse(
        iter([data]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
