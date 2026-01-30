# app/export_utils.py
"""
Export helpers (Excel + PDF)

Beginner notes:
- We generate the file in memory (BytesIO)
- Then FastAPI streams it to the browser as a download
"""

from __future__ import annotations

from io import BytesIO
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def make_export_filename(prefix: str, ext: str) -> str:
    """
    Create a clean filename like:
    inventory_items_2026-01-29_1730.xlsx
    """
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    return f"{prefix}_{stamp}.{ext}"


def items_to_xlsx_bytes(items: list[dict]) -> bytes:
    """
    Create an .xlsx file in memory.
    items is a list of dicts like:
    {"id":1,"name":"Oil Filter","sku":"TOY-...","qty":10,"price":12.5}
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory"

    headers = ["ID", "Name", "SKU", "Qty", "Price", "Total Value"]
    ws.append(headers)

    # Style header row
    header_font = Font(bold=True)
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Add data rows
    for it in items:
        price = it.get("price")
        qty = it.get("qty") or 0
        total = (qty * price) if (price is not None) else None

        ws.append([it.get("id"), it.get("name"), it.get("sku"), qty, price, total])

    # Make it readable: column widths
    widths = [8, 28, 20, 10, 12, 14]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + i)].width = w

    # Save to bytes
    bio = BytesIO()
    wb.save(bio)
    return bio.getvalue()


def items_to_pdf_bytes(items: list[dict]) -> bytes:
    """
    Create a simple A4 PDF report using ReportLab.
    """
    bio = BytesIO()

    doc = SimpleDocTemplate(
        bio,
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Inventory Report (A4)", styles["Title"]))
    story.append(Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), styles["Normal"]))
    story.append(Spacer(1, 12))

    data = [["ID", "Name", "SKU", "Qty", "Price"]]
    for it in items:
        data.append([
            str(it.get("id", "")),
            str(it.get("name", "")),
            str(it.get("sku", "")),
            str(it.get("qty", "")),
            "" if it.get("price") is None else f"{it.get('price'):.2f}",
        ])

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),  # dark header
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))

    story.append(table)
    doc.build(story)

    return bio.getvalue()
